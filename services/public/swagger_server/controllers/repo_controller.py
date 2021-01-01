import connexion

from conanci import database
from flask import abort
from swagger_server.models.inline_response2001 import InlineResponse2001  # noqa: E501
from swagger_server.models.inline_response2002 import InlineResponse2002  # noqa: E501
from swagger_server.models.repo import Repo  # noqa: E501
from swagger_server.models.repo_attributes import RepoAttributes  # noqa: F401,E501
from swagger_server.models.repo_relationships import RepoRelationships  # noqa: F401,E501
from swagger_server.models.repo_relationships_commits import RepoRelationshipsCommits  # noqa: F401,E501
from swagger_server.models.repo_relationships_commits_links import RepoRelationshipsCommitsLinks  # noqa: F401,E501
from swagger_server.models.repo_relationships_ecosystem import RepoRelationshipsEcosystem  # noqa: F401,E501
from swagger_server.models.repo_relationships_ecosystem_data import RepoRelationshipsEcosystemData  # noqa: F401,E501


def __create_repo(record: database.Repo):
    return Repo(
        id=record.id,
        type="repo",
        attributes=RepoAttributes(
            url=record.url,
            path=record.path
        ),
        relationships=RepoRelationships(
            commits=RepoRelationshipsCommits(
                links=RepoRelationshipsCommitsLinks(
                    related="repo/{0}/commit".format(record.id)
                )
            ),
            ecosystem=RepoRelationshipsEcosystem(
                data=RepoRelationshipsEcosystemData(
                    id=record.ecosystem.id,
                    type="ecosystem"
                )
            )
        )
    )


def add_repo(body=None):  # noqa: E501
    """add a new repo

     # noqa: E501

    :param body: repo to add
    :type body: dict | bytes

    :rtype: Repo
    """
    if connexion.request.is_json:
        body = Repo.from_dict(connexion.request.get_json())  # noqa: E501
        with database.session_scope() as session:
            ecosystem = session.query(database.Ecosystem)\
                .filter_by(id=body.relationships.ecosystem.data.id)\
                .first()
            if not ecosystem:
                abort(400)
            record = database.Repo()
            record.path = body.attributes.path
            record.url = body.attributes.url
            record.ecosystem = ecosystem
            session.add(record)
            session.commit()
            return __create_repo(record), 201


def delete_repo(repo_id):  # noqa: E501
    """delete a repo

     # noqa: E501

    :param repo_id: repo ID to delete
    :type repo_id: int

    :rtype: None
    """
    with database.session_scope() as session:
        record = session.query(database.Repo).filter_by(id=repo_id).first()
        if not record:
            abort(404)
        session.delete(record)
    return None


def get_repo(repo_id):  # noqa: E501
    """get a repo

     # noqa: E501

    :param repo_id: repo ID
    :type repo_id: int

    :rtype: InlineResponse2002
    """
    with database.session_scope() as session:
        record = session.query(database.Repo).filter_by(id=repo_id).first()
        if not record:
            abort(404)
        return InlineResponse2002(data=__create_repo(record))


def get_repos(ecosystem_id):  # noqa: E501
    """get repos of an ecosystem

     # noqa: E501

    :param ecosystem_id: ecosystem
    :type ecosystem_id: int

    :rtype: InlineResponse2001
    """
    with database.session_scope() as session:
        return InlineResponse2001(
            data=[__create_repo(record) for record in
                  session.query(database.Repo).filter_by(ecosystem_id=ecosystem_id).all()]
        )
