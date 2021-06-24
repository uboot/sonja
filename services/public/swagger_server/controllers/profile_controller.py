import connexion

from conanci import database
from flask import abort
from swagger_server import models


def __create_profile(record: database.Profile):
    return models.Profile(
        id=record.id,
        type="profiles",
        attributes=models.ProfileAttributes(
            name=record.name,
            container=record.container,
            docker_user=record.docker_user,
            docker_password=record.docker_password,
            settings=[models.ProfileAttributesSettings(key=r.key, value=r.value) for r in record.settings],
            options=[models.ProfileAttributesOptions(key=r.key, value=r.value) for r in record.options],
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
        record.ecosystem = ecosystem
        record.container = body.data.attributes.container
        record.docker_user = body.data.attributes.docker_user
        record.docker_password = body.data.attributes.docker_password
        record.settings = [database.Setting(s.key, s.value) for s in body.data.attributes.settings]
        record.options = [database.Option(o.key, o.value) for o in body.data.attributes.options]
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
        record.container = body.data.attributes.container
        record.docker_user = body.data.attributes.docker_user
        record.docker_password = body.data.attributes.docker_password
        record.settings = [database.Setting(s.key, s.value) for s in body.data.attributes.settings]
        record.options = [database.Option(o.key, o.value) for o in body.data.attributes.options]
        record.labels = [database.Label(l.label) for l in body.data.attributes.labels]
        return models.ProfileData(data=__create_profile(record))
