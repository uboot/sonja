import json
import re

from sonja.config import logger
from sonja.database import session_scope, Session
from sonja.model import Build, CommitStatus, Commit, Package, RecipeRevision, missing_package, BuildStatus, \
    missing_recipe, Recipe, Ecosystem
from sonja.redis import RedisClient
from typing import List


class Manager(object):
    def __init__(self, redis_client: RedisClient):
        self.__redis_client = redis_client

    def __revision_from_recipe_id(self, recipe_id):
        m = re.match("[\\w\\+\\.-]+/[\\w\\+\\.-]+(?:@\\w+/\\w+)?(#(\\w+))?", recipe_id)
        if m:
            return m.group(2) if m.group(2) else ""
        else:
            logger.error("Invalid recipe ID '%s'", recipe_id)
            return None

    def __process_recipe(self, session: Session, name: str, version: str, user: str, channel: str,
                         ecosystem: Ecosystem) -> Recipe:
        ecosystem_id = ecosystem.id
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
            session.add(recipe)

        logger.debug("Process recipe '%s' ('%s/%s@%s/%s')", recipe.id, recipe.name, recipe.version,
                     recipe.user, recipe.channel)
        return recipe

    def __process_recipe_revision(self, session: Session, name: str, version: str, user: str, channel: str,
                                  revision: str, ecosystem: Ecosystem) -> RecipeRevision:
        recipe = self.__process_recipe(session, name, version, user, channel, ecosystem)
        if not recipe:
            return None

        recipe_revision = session.query(RecipeRevision).filter_by(
            recipe_id=recipe.id,
            revision=revision
        ).first()

        if not recipe_revision:
            recipe_revision = RecipeRevision()
            recipe_revision.recipe = recipe
            recipe_revision.revision = revision
            session.add(recipe_revision)

        logger.debug("Process recipe revision '%s' (revision: '%s')", recipe_revision.id, recipe_revision.revision)
        return recipe_revision

    def __process_package(self, session: Session, package_id: str, recipe_revision: RecipeRevision)\
            -> Package:
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

    def __extract_required_packages(self, session: Session, lock_data: dict, ecosystem: Ecosystem) -> List[Package]:
        packages = []
        root = lock_data["0"]
        for requirement in root.get("requires", []) + root.get("build_requires", []):
            recipe_id = lock_data[requirement]["ref"]
            m = re.match("([\\w\\+\\.-]+)/([\\w\\+\\.-]+)(?:@(\\w+)/(\\w+))?(#(\\w+))?", recipe_id)
            if m:
                name = m.group(1)
                version = m.group(2)
                user = m.group(3)
                channel = m.group(4)
                recipe_revision = m.group(6)
            else:
                logger.error("Invalid recipe ID '%s'", recipe_id)
                return None
            package_id = lock_data[requirement]["package_id"]
            recipe_revision = self.__process_recipe_revision(session, name, version, user, channel,
                                                             recipe_revision, ecosystem)
            package = self.__process_package(session, package_id, recipe_revision)
            packages.append(package)

        return packages

    def process_success(self, build_id, build_output) -> dict:
        result = dict()

        try:
            create_data = json.loads(build_output["create"])
            logger.info("create.json")
            logger.info(build_output["create"])
        except KeyError:
            logger.error("Failed to obtain JSON output of the Conan create stage for build '%d'", build_id)
            return result

        try:
            lock_data = json.loads(build_output["lock"])["graph_lock"]["nodes"]
            logger.info("lock.json")
            logger.info(build_output["lock"])
        except KeyError:
            logger.error("Failed to obtain JSON output of the Conan lock for build '%d'", build_id)
            return result

        with session_scope() as session:
            build = session.query(Build).filter_by(id=build_id).first()
            build.package = None
            build.recipe_revision = None
            build.missing_recipes = []
            build.missing_packages = []
            for recipe_compound in create_data["installed"]:
                recipe_data = recipe_compound["recipe"]
                if recipe_data["dependency"]:
                    continue

                name = recipe_data["name"]
                version = recipe_data["version"]
                user = recipe_data.get("user", None)
                channel = recipe_data.get("channel", None)
                revision = self.__revision_from_recipe_id(recipe_data["id"])
                recipe_revision = self.__process_recipe_revision(session, name, version, user, channel, revision,
                                                                 build.profile.ecosystem)
                if not recipe_revision:
                    continue

                if build.commit.status == CommitStatus.building:
                    recipe_revision.recipe.current_revision = recipe_revision

                for package_data in recipe_compound["packages"]:
                    package_id = package_data["id"]
                    package = self.__process_package(session, package_id, recipe_revision)
                    if not package:
                        continue
                    build.package = package

                    if self.__trigger_builds_for_package(session, package):
                        result['new_builds'] = True

                if self.__trigger_builds_for_recipe(session, recipe_revision.recipe):
                    result['new_builds'] = True

            build.package.requires = self.__extract_required_packages(session, lock_data, build.profile.ecosystem)

            logger.info("Updated database for the successful build '%d'", build_id)
            return result

    def process_failure(self, build_id, build_output) -> dict:
        result = dict()
        try:
            create_data = json.loads(build_output["create"])
            logger.info("create.json")
            logger.info(build_output["create"])
        except KeyError:
            logger.info("Failed build '%d' contains no JSON output of the Conan create stage", build_id)
            return result

        try:
            lock_data = json.loads(build_output["lock"])["graph_lock"]["nodes"]
            logger.info("lock.json")
            logger.info(build_output["lock"])
        except KeyError:
            logger.info("Failed build '%d' contains no JSON output of the Conan lock", build_id)

        if not create_data["error"]:
            logger.info("Conan create for failed build '%d' was successful, no missing dependencies", build_id)

        with session_scope() as session:
            build = session.query(Build).filter_by(id=build_id).first()
            build.package = None
            build.recipe_revision = None
            build.missing_recipes = []
            build.missing_packages = []
            for recipe_compound in create_data["installed"]:
                recipe_data = recipe_compound["recipe"]
                name = recipe_data["name"]
                version = recipe_data["version"]
                user = recipe_data.get("user", None)
                channel = recipe_data.get("channel", None)
                revision = self.__revision_from_recipe_id(recipe_data["id"])

                # This is the reference data for the build. Get the data and continue
                if not recipe_data["dependency"]:
                    recipe_revision = self.__process_recipe_revision(session, name, version, user, channel, revision,
                                                                     build.profile.ecosystem)

                    if build.commit.status == CommitStatus.building:
                        recipe_revision.recipe.current_revision = recipe_revision

                    for package_data in recipe_compound["packages"]:
                        package_id = package_data["id"]
                        package = self.__process_package(session, package_id, recipe_revision)
                        if lock_data:
                            package.requires = self.__extract_required_packages(session, lock_data,
                                                                                build.profile.ecosystem)
                        build.package = package

                    if not build.package:
                        build.recipe_revision = recipe_revision

                    continue

                # This is a dependency with missing recipe. Add the missing recipe to the current build and continue
                if recipe_data["error"] and recipe_data["error"]["type"] == "missing":
                    name = recipe_data["name"]
                    version = recipe_data["version"]
                    user = recipe_data.get("user", None)
                    channel = recipe_data.get("channel", None)
                    recipe = self.__process_recipe(session, name, version, user, channel, build.profile.ecosystem)
                    build.missing_recipes.append(recipe)
                    continue

                # dependencies with missing packages remain
                recipe_revision = self.__process_recipe_revision(session, name, version, user, channel, revision,
                                                                 build.profile.ecosystem)
                if not recipe_revision:
                    continue

                for package_data in recipe_compound["packages"]:
                    if package_data["error"] and package_data["error"]["type"] == "missing":
                        package_id = package_data["id"]
                        package = self.__process_package(session, package_id, recipe_revision)
                        build.missing_packages.append(package)

            logger.info("Updated database for the failed build '%d'", build_id)
            return result
