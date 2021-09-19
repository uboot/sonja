from sonja import database
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
            user=record.user
        ),
        relationships=models.RecipeRelationships(
            ecosystem=models.RepoRelationshipsEcosystem(
                data=models.RepoRelationshipsEcosystemData(
                    id=record.ecosystem_id,
                    type="ecosystems"
                )
            ),
            revisions=models.RecipeRelationshipsRevisions(
                models.RecipeRelationshipsRevisionsLinks(
                    related="revision"
                )
            )
        )
    )


def __create_recipe_revision(record: database.RecipeRevision):
    return models.RecipeRevision(
        id=record.id,
        type="recipe-revision",
        attributes=models.RecipeRevisionAttributes(
            revision=record.revision
        ),
        relationships=models.RecipeRevisionRelationships(
            recipe=models.RecipeRevisionRelationshipsRecipe(
                data=models.RecipeRevisionRelationshipsRecipeData(
                    id=record.recipe_id,
                    type="recipes"
                )
            ),
            packages=models.RecipeRevisionRelationshipsPackages(
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


def get_recipe_revision(recipe_revision_id):
    with database.session_scope() as session:
        record = session.query(database.RecipeRevision).filter_by(id=recipe_revision_id).first()
        if not record:
            abort(404)
        return models.RecipeRevisionData(data=__create_recipe_revision(record))


def get_recipe_revisions(recipe_id):
    with database.session_scope() as session:
        records = session.query(database.RecipeRevision). \
            filter(database.RecipeRevision.recipe_id == recipe_id)
        return models.RecipeRevisionList(data=[__create_recipe_revision(record) for record in records])