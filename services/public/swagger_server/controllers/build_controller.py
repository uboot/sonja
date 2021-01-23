import connexion

from conanci import database
from flask import abort
from swagger_server import models


build_status_table = {
    "new": database.BuildStatus.new,
    "active": database.BuildStatus.active,
    "error": database.BuildStatus.error,
    "stopping": database.BuildStatus.stopping,
    "stopped": database.BuildStatus.stopped,
    "success": database.BuildStatus.success
}


def __create_build(record: database.Build):
    return models.Build(
        id=record.id,
        type="builds",
        attributes=models.BuildAttributes(
            status=record.status.name
        ),
        relationships=models.BuildRelationships(
            ecosystem=models.RepoRelationshipsEcosystem(
                models.RepoRelationshipsEcosystemData(
                    id=record.profile.ecosystem_id,
                    type="ecosystems"
                )
            ),
            commit=models.BuildRelationshipsCommit(
                data=models.BuildRelationshipsCommitData(
                    id=record.commit_id,
                    type="commits"
                )
            ),
            profile=models.BuildRelationshipsProfile(
                data=models.EcosystemRelationshipsProfilesData(
                    id=record.profile_id,
                    type="profiles"
                )
            )
        )
    )


def get_build(build_id):
    with database.session_scope() as session:
        record = session.query(database.Build).filter_by(id=build_id).first()
        if not record:
            abort(404)
        return models.BuildData(data=__create_build(record))


def get_builds(ecosystem_id):
    with database.session_scope() as session:
        # try:
        #     status = build_status_table[filter_status]
        # except KeyError:
        #     abort(400)
        records = session.query(database.Build).\
            join(database.Build.profile).\
            filter(database.Profile.ecosystem_id == ecosystem_id, database.Build.status == database.BuildStatus.active)
        return models.BuildList(data=[__create_build(record) for record in records])


def update_build(build_id, body=None):
    if connexion.request.is_json:
        body = models.BuildData.from_dict(connexion.request.get_json())  # noqa: E501

    with database.session_scope() as session:
        record = session.query(database.Build).filter_by(id=build_id).first()
        if not record:
            abort(404)
        try:
            record.status = build_status_table[body.data.attributes.status]
        except KeyError:
            abort(400)

        return models.BuildData(data=__create_build(record))
