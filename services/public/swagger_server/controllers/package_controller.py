from sonja import database
from flask import abort
from swagger_server import models


def __create_package(record: database.Package):
    return models.Package(
        id=record.id,
        type="packages",
        attributes=models.PackageAttributes(
            package_id=record.package_id
        ),
        relationships=models.PackageRelationships(
            recipe_revision=models.PackageRelationshipsReciperevision(
                data=models.PackageRelationshipsReciperevisionData(
                    id=record.recipe_revision_id,
                    type="recipe-revisions"
                )
            ),
            requires=models.RecipeRevisionRelationshipsPackages(
                data=[
                    models.BuildRelationshipsPackageData(
                        id=package.id,
                        type="packages"
                    ) for package in record.requires
                ]
            ),
            required_by=models.RecipeRevisionRelationshipsPackages(
                data=[
                    models.BuildRelationshipsPackageData(
                        id=package.id,
                        type="packages"
                    ) for package in record.required_by
                ]
            )
        )
    )


def get_package(package_id):
    with database.session_scope() as session:
        record = session.query(database.Package).filter_by(id=package_id).first()
        if not record:
            abort(404)
        return models.PackageData(data=__create_package(record))
