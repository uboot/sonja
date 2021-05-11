from conanci import database
from flask import abort
from swagger_server import models


def __create_recipe(record: database.Recipe):
    return models.Recipe(
        id=record.id,
        type="recipes",
        attributes=models.RecipeAttributes(
            name=record.name,
            version=record.version,
            channel=record.channel,
            user=record.user,
            revision=record.revision
        ),
        relationships=models.RecipeRelationships(
            ecosystem=models.RepoRelationshipsEcosystem(
                data=models.RepoRelationshipsEcosystemData(
                    id=record.ecosystem_id,
                    type="ecosystems"
                )
            ),
            packages=models.BuildRelationshipsMissingpackages(
                data=[
                    models.BuildRelationshipsPackageData(
                        id=package.id,
                        type="packages"
                    ) for package in record.packages
                ]
            )
        )
    )


def get_recipe(recipe_id):
    with database.session_scope() as session:
        record = session.query(database.Recipe).filter_by(id=recipe_id).first()
        if not record:
            abort(404)
        return models.RecipeData(data=__create_recipe(record))


def get_recipes(ecosystem_id):
    with database.session_scope() as session:
        records = session.query(database.Recipe). \
            filter(database.Recipe.ecosystem_id == ecosystem_id)
        return models.EcosystemList(data=[__create_recipe(record) for record in records])
