import connexion

from sonja import database
from sonja.ssh import encode, generate_rsa_key
from flask import abort
from swagger_server import models


def __create_ecosystem(record: database.Ecosystem):
    return models.Ecosystem(
        id=str(record.id),
        type="ecosystems",
        attributes=models.EcosystemAttributes(
            name=record.name,
            user=record.user,
            conan_config_url=record.conan_config_url,
            conan_config_branch=record.conan_config_branch,
            conan_config_path=record.conan_config_path,
            conan_remote=record.conan_remote,
            conan_user=record.conan_user,
            conan_password=record.conan_password,
            public_ssh_key=record.public_ssh_key,
            known_hosts=record.known_hosts,
            credentials=[models.EcosystemAttributesCredentials(url=c.url, password=c.password, username=c.username)
                         for c in record.credentials]
        ),
        relationships=models.EcosystemRelationships(
            builds=models.EcosystemRelationshipsBuilds(
                links=models.EcosystemRelationshipsBuildsLinks(
                    related="build"
                )
            ),
            channels=models.EcosystemRelationshipsChannels(
                data=[
                    models.EcosystemRelationshipsChannelsData(
                        id=channel.id,
                        type="channels"
                    ) for channel in record.channels
                 ]
            ),
            profiles=models.EcosystemRelationshipsProfiles(
                data=[
                    models.EcosystemRelationshipsProfilesData(
                        id=profile.id,
                        type="profiles"
                    ) for profile in record.profiles
                ]
            ),
            repos=models.EcosystemRelationshipsRepos(
                links=models.EcosystemRelationshipsReposLinks(
                    related="repo"
                )
            ),
            recipes=models.EcosystemRelationshipsRecipes(
                links=models.EcosystemRelationshipsRecipesLinks(
                    related="recipe"
                )
            )
        )
    )


def add_ecosystem(body=None):
    if connexion.request.is_json:
        body = models.EcosystemData.from_dict(connexion.request.get_json())  # noqa: E501

    record = database.Ecosystem()
    record.name = body.data.attributes.name
    record.user = body.data.attributes.user
    record.conan_config_url = body.data.attributes.conan_config_url
    record.conan_config_branch = body.data.attributes.conan_config_branch
    record.conan_config_path = body.data.attributes.conan_config_path
    record.conan_remote = body.data.attributes.conan_remote
    record.conan_user = body.data.attributes.conan_user
    record.conan_password = body.data.attributes.conan_password
    record.known_hosts = body.data.attributes.known_hosts
    private, public = generate_rsa_key()
    record.ssh_key = encode(private)
    record.public_ssh_key = encode(public)
    credentials = []
    if body.data.attributes.credentials:
        for c in body.data.attributes.credentials:
            git_credential = database.GitCredential()
            git_credential.url = c.url
            git_credential.username = c.username
            git_credential.password = c.password
            credentials.append(git_credential)
    record.credentials = credentials
    with database.session_scope() as session:
        session.add(record)
        session.commit()
        return models.EcosystemData(data=__create_ecosystem(record)), 201


def delete_ecosystem(ecosystem_id):
    with database.session_scope() as session:
        record = session.query(database.Ecosystem).filter_by(id=ecosystem_id).first()
        if not record:
            abort(404)
        session.delete(record)
    return None


def get_ecosystem(ecosystem_id):
    with database.session_scope() as session:
        record = session.query(database.Ecosystem).filter_by(id=ecosystem_id).first()
        if not record:
            abort(404)
        return models.EcosystemData(data=__create_ecosystem(record))


def get_ecosystems():
    with database.session_scope() as session:
        return models.EcosystemList(
            data=[__create_ecosystem(record) for record in session.query(database.Ecosystem).all()]
        )


def update_ecosystem(ecosystem_id, body=None):
    if connexion.request.is_json:
        body = models.EcosystemData.from_dict(connexion.request.get_json())  # noqa: E501

    with database.session_scope() as session:
        record = session.query(database.Ecosystem).filter_by(id=ecosystem_id).first()
        if not record:
            abort(404)

        record.name = body.data.attributes.name
        record.user = body.data.attributes.user
        record.conan_config_url = body.data.attributes.conan_config_url
        record.conan_config_branch = body.data.attributes.conan_config_branch
        record.conan_config_path = body.data.attributes.conan_config_path
        record.conan_remote = body.data.attributes.conan_remote
        record.conan_user = body.data.attributes.conan_user
        record.conan_password = body.data.attributes.conan_password
        record.known_hosts = body.data.attributes.known_hosts
        if body.data.attributes.credentials:
            credentials = []
            for c in body.data.attributes.credentials:
                git_credential = database.GitCredential()
                git_credential.url = c.url
                git_credential.username = c.username
                git_credential.password = c.password
                credentials.append(git_credential)
            record.credentials = credentials
        if body.data.attributes.public_ssh_key == '':
            private, public = generate_rsa_key()
            record.ssh_key = encode(private)
            record.public_ssh_key = encode(public)

        return models.EcosystemData(data=__create_ecosystem(record))
