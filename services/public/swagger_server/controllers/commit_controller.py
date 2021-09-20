from sonja import database
from flask import abort
from swagger_server import models


def __create_commit(record: database.Commit):
    return models.Commit(
        id=str(record.id),
        type="commits",
        attributes=models.CommitAttributes(
            sha=record.sha,
            message=record.message,
            user_name=record.user_name,
            user_email=record.user_email
        ),
        relationships=models.CommitRelationships(
            repo=models.CommitRelationshipsRepo(
                data=models.CommitRelationshipsRepoData(
                    id=record.repo_id,
                    type="repos"
                )
            ),
            channel=models.CommitRelationshipsChannel(
                data=models.EcosystemRelationshipsChannelsData(
                    id=record.channel_id,
                    type="channels"
                )
            ),
            builds=models.CommitRelationshipsBuilds(
                data=[
                    models.CommitRelationshipsBuildsData(
                        id=build.id,
                        type="builds"
                    ) for build in record.builds
                ]
            )
        )
    )

def get_commit(commit_id):
    with database.session_scope() as session:
        record = session.query(database.Commit).filter_by(id=commit_id).first()
        if not record:
            abort(404)
        return models.CommitData(data=__create_commit(record))


def get_commits(repo_id):
    with database.session_scope() as session:
        return models.CommitList(
            data=[__create_commit(record) for record in
                  session.query(database.Commit).filter_by(repo_id=repo_id).all()]
        )
