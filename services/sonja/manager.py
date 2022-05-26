import json
import re

from sonja.config import logger
from sonja.database import session_scope, Session
from sonja.model import Build, CommitStatus, Commit, Package, RecipeRevision, missing_package, BuildStatus, \
    missing_recipe, Recipe, Ecosystem
from sonja.redis import RedisClient


class Manager(object):
    def __init__(self, redis_client: RedisClient):
        self.__redis_client = redis_client

    def __process_recipe(self, session: Session, recipe_data: dict, ecosystem: Ecosystem) -> Recipe:
        ecosystem_id = ecosystem.id
        name = recipe_data["name"]
        version = recipe_data["version"]
        user = recipe_data.get("user", None)
        channel = recipe_data.get("channel", None)

        recipe = session.query(Recipe).filter_by(
            ecosystem_id=ecosystem_id,
            name=name,
            version=version,
            user=user,
            channel=channel
        ).first()

        if not recipe:
            recipe = Recipe()
            recipe.ecosystem = ecosystem
            recipe.name = name
            recipe.version = version
            recipe.user = user
            recipe.channel = channel

        logger.debug("Process recipe '%s' ('%s/%s@%s/%s')", recipe.id, recipe.name, recipe.version,
                     recipe.user, recipe.channel)
        return recipe

    def __process_recipe_revision(self, session: Session, recipe_data: dict, ecosystem: Ecosystem) -> RecipeRevision:
        recipe = self.__process_recipe(session, recipe_data, ecosystem)
        if not recipe:
            return None

        m = re.match("[\\w\\+\\.-]+/[\\w\\+\\.-]+(?:@\\w+/\\w+)?(#(\\w+))?", recipe_data["id"])
        if m:
            revision = m.group(2) if m.group(2) else ""
        else:
            logger.error("Invalid recipe ID '%s'", recipe_data["id"])
            return None

        recipe_revision = session.query(RecipeRevision).filter_by(
            recipe_id=recipe.id,
            revision=revision
        ).first()

        if not recipe_revision:
            recipe_revision = RecipeRevision()
            recipe_revision.recipe = recipe
            recipe_revision.revision = revision

        logger.debug("Process recipe revision '%s' (revision: '%s')", recipe_revision.id, recipe_revision.revision)
        return recipe_revision

    def __process_package(self, session: Session, package_data: dict, recipe_revision: RecipeRevision)\
            -> Package:
        package_id = package_data["id"]
        package = session.query(Package).filter_by(
            package_id=package_id,
            recipe_revision_id=recipe_revision.id
        ).first()

        if not package:
            package = Package()
            package.package_id = package_id
            package.recipe_revision = recipe_revision
            session.add(package)

        logger.debug("Process package '%s' (ID: '%s')", package.id, package.package_id)
        return package

    def __trigger_builds_for_recipe(self, session: Session, recipe: Recipe):
        logger.debug("Trigger builds for recipe '%s' ('%s/%s@%s/%s')", recipe.id, recipe.name, recipe.version,
                     recipe.user, recipe.channel)

        # get all failed builds which are waiting for this recipe
        builds = session.query(Build).filter(Build.status == BuildStatus.error).\
            filter(missing_recipe.columns['build_id'] == Build.id).\
            filter(missing_recipe.columns['recipe_id'] == recipe.id).\
            filter(Build.commit_id == Commit.id).\
            filter(Commit.status == CommitStatus.building).\
            all()

        # re-trigger these builds
        for build in builds:
            logger.info("Set status of build '%d' to 'new'", build.id)
            build.status = BuildStatus.new

        session.commit()
        if builds:
            self.__redis_client.publish_build_updates(builds)

        return builds

    def __trigger_builds_for_package(self, session: Session, package: Package):
        logger.debug("Trigger builds for package '%s' (ID: '%s')", package.id, package.package_id)

        # Get all failed builds which are waiting a package of the same recipe revision. In these cases the package ID
        # should match exactly.
        same_recipe_revision = session.query(Build).filter(Build.status == BuildStatus.error).\
            filter(missing_package.columns['build_id'] == Build.id).\
            filter(missing_package.columns['package_id'] == package.id).\
            filter(Build.commit_id == Commit.id).\
            filter(Commit.status == CommitStatus.building).\
            all()

        # Get all failed builds which are waiting for a package of the same recipe but a different recipe revision.
        # In these cases a build is triggered regardless of the exact package ID (because the package ID might be
        # computed differently for a different recipe revision).
        different_recipe_revision = session.query(Build).\
            filter(Build.status == BuildStatus.error).\
            filter(missing_package.columns['build_id'] == Build.id).\
            filter(missing_package.columns['package_id'] == Package.id).\
            filter(Build.commit_id == Commit.id).\
            filter(Commit.status == CommitStatus.building).\
            filter(Package.recipe_revision_id == RecipeRevision.id).\
            filter(RecipeRevision.revision != package.recipe_revision.revision).\
            filter(RecipeRevision.recipe_id == package.recipe_revision.recipe.id).\
            all()

        # re-trigger these builds
        builds = same_recipe_revision + different_recipe_revision
        for build in builds:
            logger.info("Set status of build '%d' to 'new'", build.id)
            build.status = BuildStatus.new

        session.commit()
        if builds:
            self.__redis_client.publish_build_updates(builds)

        return builds

    def process_success(self, build_id, build_output) -> dict:
        result = dict()

        try:
            data = json.loads(build_output["create"])
        except KeyError:
            logger.error("Failed to obtain JSON output of the Conan create stage for build '%d'", build_id)
            return result

        with session_scope() as session:
            build = session.query(Build).filter_by(id=build_id).first()
            build.package = None
            build.missing_recipes = []
            build.missing_packages = []
            for recipe_compound in data["installed"]:
                recipe_data = recipe_compound["recipe"]
                if recipe_data["dependency"]:
                    continue

                recipe_revision = self.__process_recipe_revision(session, recipe_data, build.profile.ecosystem)
                if not recipe_revision:
                    continue

                for package_data in recipe_compound["packages"]:
                    package = self.__process_package(session, package_data, recipe_revision)
                    if not package:
                        continue
                    build.package = package

                    if self.__trigger_builds_for_package(session, package):
                        result['new_builds'] = True

                if self.__trigger_builds_for_recipe(session, recipe_revision.recipe):
                    result['new_builds'] = True

            logger.info("Updated database for the successful build '%d'", build_id)
            return result

    def process_failure(self, build_id, build_output) -> dict:
        result = dict()
        try:
            data = json.loads(build_output["create"])
        except KeyError:
            logger.info("Failed build contains no JSON output of the Conan create stage")
            return result

        if not data["error"]:
            logger.info("Conan create for failed build '%d' was successful, no missing dependencies", build_id)

        with session_scope() as session:
            build = session.query(Build).filter_by(id=build_id).first()
            build.package = None
            build.missing_recipes = []
            build.missing_packages = []
            for recipe_compound in data["installed"]:
                recipe_data = recipe_compound["recipe"]
                if not recipe_data["dependency"]:
                    continue

                if recipe_data["error"] and recipe_data["error"]["type"] == "missing":
                    recipe = self.__process_recipe(session, recipe_data, build.profile.ecosystem)
                    build.missing_recipes.append(recipe)
                    continue

                recipe_revision = self.__process_recipe_revision(session, recipe_data, build.profile.ecosystem)
                if not recipe_revision:
                    continue

                for package_data in recipe_compound["packages"]:
                    if package_data["error"] and package_data["error"]["type"] == "missing":
                        package = self.__process_package(session, package_data, recipe_revision)
                        build.missing_packages.append(package)

            logger.info("Updated database for the failed build '%d'", build_id)
            return result
