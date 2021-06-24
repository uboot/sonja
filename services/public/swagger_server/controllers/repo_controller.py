import connexion

from conanci import database
from flask import abort
from swagger_server import models


def __create_repo(record: database.Repo):
    return models.Repo(
        id=record.id,
        type="repos",
        attributes=models.RepoAttributes(
            name=record.name,
            url=record.url,
            path=record.path,
            exclude=[models.RepoAttributesExclude(label=r.value) for r in record.exclude]
        ),
        relationships=models.RepoRelationships(
            commits=models.RepoRelationshipsCommits(
                links=models.RepoRelationshipsCommitsLinks(
                    related="commit".format(record.id)
                )
            ),
            ecosystem=models.RepoRelationshipsEcosystem(
                data=models.RepoRelationshipsEcosystemData(
                    id=record.ecosystem.id,
                    type="ecosystems"
                )
            )
        )
    )


def add_repo(body=None):
    if connexion.request.is_json:
        body = models.RepoData.from_dict(connexion.request.get_json())  # noqa: E501

    with database.session_scope() as session:
        ecosystem = session.query(database.Ecosystem)\
            .filter_by(id=body.data.relationships.ecosystem.data.id)\
            .first()
        if not ecosystem:
            abort(400)
        record = database.Repo()
        record.name = body.data.attributes.name
        record.path = body.data.attributes.path
        record.url = body.data.attributes.url
        record.exclude = [database.Label(l.label) for l in body.data.attributes.exclude]
        record.ecosystem = ecosystem
        session.add(record)
        session.commit()
        return models.RepoData(data=__create_repo(record)), 201


def delete_repo(repo_id):
    with database.session_scope() as session:
        record = session.query(database.Repo).filter_by(id=repo_id).first()
        if not record:
            abort(404)
        session.delete(record)
    return None


def get_repo(repo_id):
    with database.session_scope() as session:
        record = session.query(database.Repo).filter_by(id=repo_id).first()
        if not record:
            abort(404)
        return models.RepoData(data=__create_repo(record))


def get_repos(ecosystem_id):
    with database.session_scope() as session:
        return models.RepoList(
            data=[__create_repo(record) for record in
                  session.query(database.Repo).filter_by(ecosystem_id=ecosystem_id).all()]
        )

def update_repo(repo_id, body=None):
    if connexion.request.is_json:
        body = models.RepoData.from_dict(connexion.request.get_json())  # noqa: E501

    with database.session_scope() as session:
        record = session.query(database.Repo).filter_by(id=repo_id).first()
        if not record:
            abort(404)

        record.name = body.data.attributes.name
        record.path = body.data.attributes.path
        record.url = body.data.attributes.url
        record.exclude = [database.Label(l.label) for l in body.data.attributes.exclude]
        return models.RepoData(data=__create_repo(record))

