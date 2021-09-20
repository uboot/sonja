import connexion

from sonja import database
from flask import abort
from swagger_server import models


platform_table = {
    "linux": database.Platform.linux,
    "windows": database.Platform.windows
}


def __create_profile(record: database.Profile):
    return models.Profile(
        id=str(record.id),
        type="profiles",
        attributes=models.ProfileAttributes(
            name=record.name,
            container=record.container,
            platform=record.platform.name if record.platform else "",
            conan_profile=record.conan_profile,
            docker_user=record.docker_user,
            docker_password=record.docker_password,
            labels=[models.RepoAttributesExclude(label=r.value) for r in record.labels]
        ),
        relationships=models.ProfileRelationships(
            ecosystem=models.RepoRelationshipsEcosystem(
                data=models.RepoRelationshipsEcosystemData(
                    id=record.ecosystem_id,
                    type="ecosystems"
                )
            )
        )
    )


def add_profile(body=None):
    if connexion.request.is_json:
        body = models.ProfileData.from_dict(connexion.request.get_json())  # noqa: E501

    with database.session_scope() as session:
        ecosystem = session.query(database.Ecosystem)\
            .filter_by(id=body.data.relationships.ecosystem.data.id)\
            .first()
        if not ecosystem:
            abort(400)
        record = database.Profile()
        record.name = body.data.attributes.name
        record.platform = platform_table[body.data.attributes.platform]
        record.ecosystem = ecosystem
        record.container = body.data.attributes.container
        record.conan_profile = body.data.attributes.conan_profile
        record.docker_user = body.data.attributes.docker_user
        record.docker_password = body.data.attributes.docker_password
        record.labels = [database.Label(l.label) for l in body.data.attributes.labels]
        session.add(record)
        session.commit()
        return models.ProfileData(data=__create_profile(record)), 201


def delete_profile(profile_id):
    with database.session_scope() as session:
        record = session.query(database.Profile).filter_by(id=profile_id).first()
        if not record:
            abort(404)
        session.delete(record)
    return None


def get_profile(profile_id):
    with database.session_scope() as session:
        record = session.query(database.Profile).filter_by(id=profile_id).first()
        if not record:
            abort(404)
        return models.ProfileData(data=__create_profile(record))


def update_profile(profile_id, body=None):
    if connexion.request.is_json:
        body = models.ProfileData.from_dict(connexion.request.get_json())  # noqa: E501

    with database.session_scope() as session:
        record = session.query(database.Profile).filter_by(id=profile_id).first()
        if not record:
            abort(404)

        record.name = body.data.attributes.name
        record.platform = platform_table[body.data.attributes.platform]
        record.conan_profile = body.data.attributes.conan_profile
        record.container = body.data.attributes.container
        record.docker_user = body.data.attributes.docker_user
        record.docker_password = body.data.attributes.docker_password
        record.labels = [database.Label(l.label) for l in body.data.attributes.labels]
        return models.ProfileData(data=__create_profile(record))
