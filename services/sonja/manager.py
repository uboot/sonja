import json
import re

from sonja import database


def _process_recipe(session: database.Session, recipe_data: dict, build: database.Build) -> database.Recipe:
    if recipe_data["dependency"]:
        return None
    ecosystem_id = build.profile.ecosystem_id
    name = recipe_data["name"]
    version = recipe_data["version"]
    user = recipe_data.get("user", None)
    channel = recipe_data.get("channel", None)

    recipe = session.query(database.Recipe).filter_by(
        ecosystem_id=ecosystem_id,
        name=name,
        version=version,
        user=user,
        channel=channel
    ).first()

    if recipe:
        return recipe

    recipe = database.Recipe()
    recipe.ecosystem = build.profile.ecosystem
    recipe.name = name
    recipe.version = version
    recipe.user = user
    recipe.channel = channel

    return recipe


def _process_recipe_revision(session: database.Session, recipe_data: dict, build: database.Build)\
        -> database.RecipeRevision:
    if recipe_data["dependency"]:
        return None

    recipe = _process_recipe(session, recipe_data, build)
    if not recipe:
        return None

    m = re.match("[\\w\\+\\.-]+/[\\w\\+\\.-]+(?:@\\w+/\\w+)?#(\\w+)", recipe_data["id"])
    revision = None
    if m:
        revision = m.group(1)

    recipe_revision = session.query(database.RecipeRevision).filter_by(
        recipe_id=recipe.id,
        revision=revision
    ).first()

    if recipe_revision:
        return recipe_revision

    recipe_revision = database.RecipeRevision()
    recipe_revision.recipe = recipe
    recipe_revision.revision = revision

    return recipe_revision


def _process_package(session: database.Session, package_data: dict, recipe_revision: database.RecipeRevision) -> database.Package:
    package_id = package_data["id"]
    package = session.query(database.Package).filter_by(
        package_id=package_id,
        recipe_revision_id=recipe_revision.id
    ).first()

    if package:
        return package

    package = database.Package()
    package.package_id = package_id
    package.recipe_revision = recipe_revision
    return package


def process(build_id, build_output):
    data = json.loads(build_output["create"])
    with database.session_scope() as session:
        build = session.query(database.Build).filter_by(id=build_id).first()
        for recipe_compound in data["installed"]:
            recipe_data = recipe_compound["recipe"]
            recipe_revision = _process_recipe_revision(session, recipe_data, build)
            if not recipe_revision:
                continue
            for package_data in recipe_compound["packages"]:
                package = _process_package(session, package_data, recipe_revision)
                if not package:
                    continue
                build.package = package
            session.add(recipe_revision)
