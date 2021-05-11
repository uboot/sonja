import json
import re

from conanci import database


def _process_recipe(session: database.Session, recipe_data: dict, build: database.Build) -> database.Recipe:
    if recipe_data["dependency"]:
        return None
    ecosystem_id = build.profile.ecosystem_id
    name = recipe_data["name"]
    version = recipe_data["version"]
    user = recipe_data.get("user", None)
    channel = recipe_data.get("channel", None)
    m = re.match("[\\w\\+\\.-]+/[\\w\\+\\.-]+(?:@\\w+/\\w+)?#(\\w+)", recipe_data["id"])
    revision = None
    if m:
        revision = m.group(1)

    recipe = session.query(database.Recipe).filter_by(
        ecosystem_id=ecosystem_id,
        name=name,
        version=version,
        user=user,
        channel=channel,
        revision=revision
    ).first()

    if recipe:
        return recipe

    recipe = database.Recipe()
    recipe.ecosystem = build.profile.ecosystem
    recipe.name = name
    recipe.version = version
    recipe.user = user
    recipe.channel = channel
    recipe.revision = revision

    return recipe


def _process_package(session: database.Session, package_data: dict, recipe: database.Recipe) -> database.Package:
    package_id = package_data["id"]
    package = session.query(database.Package).filter_by(
        package_id=package_id,
        recipe_id=recipe.id
    ).first()

    if package:
        return package

    package = database.Package()
    package.package_id = package_id
    package.recipe = recipe
    return package


def process(build_id, build_output):
    data = json.loads(build_output["create"])
    with database.session_scope() as session:
        build = session.query(database.Build).filter_by(id=build_id).first()
        for recipe_compound in data["installed"]:
            recipe_data = recipe_compound["recipe"]
            recipe = _process_recipe(session, recipe_data, build)
            if not recipe:
                continue
            for package_data in recipe_compound["packages"]:
                package = _process_package(session, package_data, recipe)
                if not package:
                    continue
                build.package = package
            session.add(recipe)
