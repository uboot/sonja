import connexion

from conanci import database
from flask import abort

from swagger_server.models import BuildAttributes, BuildRelationships, BuildRelationshipsCommitData, \
    BuildRelationshipsProfileData
from swagger_server.models.build import Build  # noqa: E501
from swagger_server.models.inline_response20010 import InlineResponse20010
from swagger_server.models.inline_response2009 import InlineResponse2009  # noqa: E501
from swagger_server.models.build_relationships_commit import BuildRelationshipsCommit  # noqa: F401,E501
from swagger_server.models.build_relationships_profile import BuildRelationshipsProfile  # noqa: F401,E501


build_status_table = {
    "new": database.BuildStatus.new,
    "active": database.BuildStatus.active,
    "error": database.BuildStatus.error,
    "stopping": database.BuildStatus.stopping,
    "stopped": database.BuildStatus.stopped,
    "success": database.BuildStatus.success
}


def __create_build(record: database.Build):
    return Build(
        id=record.id,
        type="build",
        attributes=BuildAttributes(
            status=record.status.name
        ),
        relationships=BuildRelationships(
            commit=BuildRelationshipsCommit(
                data=BuildRelationshipsCommitData(
                    id=record.commit_id,
                    type="commit"
                )
            ),
            profile=BuildRelationshipsProfile(
                data=BuildRelationshipsProfileData(
                    id=record.profile_id,
                    type="profile"
                )
            )
        )
    )


def get_builds(ecosystem_id, filter_status=None):  # noqa: E501
    """get builds of an ecosystem

     # noqa: E501

    :param ecosystem_id: ecosystem
    :type ecosystem_id: int
    :param filter_status: build status
    :type filter_status: str

    :rtype: InlineResponse2009
    """
    with database.session_scope() as session:
        try:
            status = build_status_table[filter_status]
        except KeyError:
            abort(400)
        records = session.query(database.Build).\
            join(database.Build.profile).\
            filter(database.Profile.ecosystem_id == ecosystem_id, database.Build.status == status)
        return InlineResponse2009(data=[__create_build(record) for record in records])


def update_build(build_id, body=None):  # noqa: E501
    """update a build

     # noqa: E501

    :param build_id: id of the build to update
    :type build_id: int
    :param body: updated build data
    :type body: dict | bytes

    :rtype: InlineResponse20010
    """
    if connexion.request.is_json:
        body = Build.from_dict(connexion.request.get_json())  # noqa: E501
    with database.session_scope() as session:
        record = session.query(database.Build).filter_by(id=build_id).first()
        if not record:
            abort(404)
        try:
            record.status = build_status_table[body.attributes.status]
        except KeyError:
            abort(400)

        return InlineResponse20010(
            data=__create_build(record)
        )
