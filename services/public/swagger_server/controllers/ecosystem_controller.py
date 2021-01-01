import connexion

from conanci import database
from conanci.ssh import encode, generate_rsa_key
from flask import abort
from swagger_server.models.ecosystem import Ecosystem  # noqa: E501
from swagger_server.models.ecosystem_attributes import EcosystemAttributes  # noqa: F401,E501
from swagger_server.models.ecosystem_relationships import EcosystemRelationships  # noqa: F401,E501
from swagger_server.models.ecosystem_relationships_builds import EcosystemRelationshipsBuilds  # noqa: F401,E501
from swagger_server.models.ecosystem_relationships_builds_links import EcosystemRelationshipsBuildsLinks  # noqa: F401,E501
from swagger_server.models.ecosystem_relationships_channels import EcosystemRelationshipsChannels  # noqa: F401,E501
from swagger_server.models.ecosystem_relationships_channels_links import EcosystemRelationshipsChannelsLinks  # noqa: F401,E501
from swagger_server.models.ecosystem_relationships_profiles import EcosystemRelationshipsProfiles  # noqa: F401,E501
from swagger_server.models.ecosystem_relationships_profiles_links import EcosystemRelationshipsProfilesLinks  # noqa: F401,E501
from swagger_server.models.ecosystem_relationships_repos import EcosystemRelationshipsRepos  # noqa: F401,E501
from swagger_server.models.ecosystem_relationships_repos_links import EcosystemRelationshipsReposLinks  # noqa: F401,E501
from swagger_server.models.inline_response200 import InlineResponse200  # noqa: E501


def __create_ecosystem(record: database.Ecosystem):
    return Ecosystem(
        id=record.id,
        type="ecosystem",
        attributes=EcosystemAttributes(
            name=record.name,
            user=record.user,
            settings=record.settings,
            public_ssh_key=record.public_ssh_key,
            known_hosts=record.known_hosts
        ),
        relationships=EcosystemRelationships(
            builds=EcosystemRelationshipsBuilds(
                links=EcosystemRelationshipsBuildsLinks(
                    related="ecosystem/{0}/build".format(record.id)
                )
            ),
            channels=EcosystemRelationshipsChannels(
                links=EcosystemRelationshipsChannelsLinks(
                    related="ecosystem/{0}/channel".format(record.id)
                )
            ),
            profiles=EcosystemRelationshipsProfiles(
                links=EcosystemRelationshipsProfilesLinks(
                    related="ecosystem/{0}/profile".format(record.id)
                )
            ),
            repos=EcosystemRelationshipsRepos(
                links=EcosystemRelationshipsReposLinks(
                    related="ecosystem/{0}/repo".format(record.id)
                )
            )
        )
    )


def add_ecosystem(body=None):  # noqa: E501
    """add a new ecosystem

     # noqa: E501

    :param body: ecosystem to add
    :type body: dict | bytes

    :rtype: Ecosystem
    """
    if connexion.request.is_json:
        body = Ecosystem.from_dict(connexion.request.get_json())  # noqa: E501
        record = database.Ecosystem()
        record.name = body.attributes.name
        record.user = body.attributes.user
        record.known_hosts = body.attributes.known_hosts
        private, public = generate_rsa_key()
        record.ssh_key = encode(private)
        record.public_ssh_key = encode(public)
        record.settings = body.attributes.settings
        with database.session_scope() as session:
            session.add(record)
            session.commit()
            return __create_ecosystem(record), 201


def delete_ecosystem(ecosystem_id):  # noqa: E501
    """delete an ecosystem

     # noqa: E501

    :param ecosystem_id: ecosystem id to delete
    :type ecosystem_id: int

    :rtype: None
    """
    with database.session_scope() as session:
        record = session.query(database.Ecosystem).filter_by(id=ecosystem_id).first()
        if not record:
            abort(404)
        session.delete(record)
    return None


def get_ecosystems():  # noqa: E501
    """get all ecosystems

     # noqa: E501


    :rtype: InlineResponse200
    """
    with database.session_scope() as session:
        return InlineResponse200(
            data=[__create_ecosystem(record) for record in session.query(database.Ecosystem).all()]
        )


def update_ecosystem(ecosystem_id, body=None):  # noqa: E501
    """update an ecosystem

     # noqa: E501

    :param ecosystem_id: id of the ecosystem to update
    :type ecosystem_id: int
    :param body: updated ecosystem data
    :type body: dict | bytes

    :rtype: Ecosystem
    """
    if connexion.request.is_json:
        body = Ecosystem.from_dict(connexion.request.get_json())  # noqa: E501

    with database.session_scope() as session:
        record = session.query(database.Ecosystem).filter_by(id=ecosystem_id).first()
        if not record:
            abort(404)

        record.name = body.attributes.name
        record.user = body.attributes.user
        record.known_hosts = body.attributes.known_hosts
        if body.attributes.public_ssh_key == '':
            private, public = generate_rsa_key()
            record.ssh_key = encode(private)
            record.public_ssh_key = encode(public)
        record.settings = body.attributes.settings

        return __create_ecosystem(record)
