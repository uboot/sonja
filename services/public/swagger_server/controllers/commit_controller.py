from conanci import database
from flask import abort
from swagger_server.models import CommitAttributes, CommitRelationships, CommitRelationshipsRepoData, \
    CommitRelationshipsChannelData
from swagger_server.models.commit import Commit
from swagger_server.models.commit_relationships_channel import CommitRelationshipsChannel  # noqa: F401,E501
from swagger_server.models.commit_relationships_repo import CommitRelationshipsRepo  # noqa: F401,E501
from swagger_server.models.inline_response2005 import InlineResponse2005  # noqa: E501
from swagger_server.models.inline_response2006 import InlineResponse2006  # noqa: E501


def __create_commit(record: database.Commit):
    return Commit(
        id=record.id,
        type="commit",
        attributes=CommitAttributes(
            sha=record.sha
        ),
        relationships=CommitRelationships(
            repo=CommitRelationshipsRepo(
                data=CommitRelationshipsRepoData(
                    id=record.repo_id,
                    type="repo"
                )
            ),
            channel=CommitRelationshipsChannel(
                data=CommitRelationshipsChannelData(
                    id=record.channel_id,
                    type="channel"
                )
            )
        )
    )

def get_commit(commit_id):  # noqa: E501
    """get a commit

     # noqa: E501

    :param commit_id: commite ID
    :type commit_id: int

    :rtype: InlineResponse2006
    """
    with database.session_scope() as session:
        record = session.query(database.Commit).filter_by(id=commit_id).first()
        if not record:
            abort(404)
        return InlineResponse2006(data=__create_commit(record))


def get_commits(repo_id):  # noqa: E501
    """get the commits of a repo

     # noqa: E501

    :param repo_id: repo
    :type repo_id: int

    :rtype: InlineResponse2005
    """
    with database.session_scope() as session:
        return InlineResponse2005(
            data=[__create_commit(record) for record in
                  session.query(database.Commit).filter_by(repo_id=repo_id).all()]
        )
