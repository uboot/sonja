import connexion

from conanci import database
from flask import abort
from swagger_server.models import ChannelAttributes, ProfileRelationships, RepoRelationshipsEcosystem, \
    RepoRelationshipsEcosystemData
from swagger_server.models.channel import Channel  # noqa: E501
from swagger_server.models.inline_response2007 import InlineResponse2007  # noqa: E501
from swagger_server.models.inline_response2008 import InlineResponse2008  # noqa: E501


def __createChannel(record: database.Channel):
    return Channel(
        id=record.id,
        type="channel",
        attributes=ChannelAttributes(
            name=record.name,
            branch=record.branch
        ),
        relationships=ProfileRelationships(
            ecosystem=RepoRelationshipsEcosystem(
                data=RepoRelationshipsEcosystemData(
                    id=record.ecosystem_id,
                    type="ecosystem"
                )
            )
        )
    )


def add_channel(body=None):  # noqa: E501
    """add a new channel

     # noqa: E501

    :param body: channel to add
    :type body: dict | bytes

    :rtype: Channel
    """
    if connexion.request.is_json:
        body = Channel.from_dict(connexion.request.get_json())  # noqa: E501
        with database.session_scope() as session:
            ecosystem = session.query(database.Ecosystem).filter_by(id=body.relationships.ecosystem.data.id).first()
            if not ecosystem:
                abort(400)
            record = database.Channel()
            record.name = body.attributes.name
            record.ecosystem = ecosystem
            record.branch = body.attributes.branch
            session.add(record)
            session.commit()
            return __createChannel(record), 201


def delete_channel(channel_id):  # noqa: E501
    """delete a channel

     # noqa: E501

    :param channel_id: channel ID to delete
    :type channel_id: int

    :rtype: None
    """
    with database.session_scope() as session:
        record = session.query(database.Channel).filter_by(id=channel_id).first()
        if not record:
            abort(404)
        session.delete(record)
    return None


def get_channel(channel_id):  # noqa: E501
    """get a channel

     # noqa: E501

    :param channel_id: channel ID
    :type channel_id: int

    :rtype: InlineResponse2008
    """
    with database.session_scope() as session:
        record = session.query(database.Channel).filter_by(id=channel_id).first()
        if not record:
            abort(404)
        return InlineResponse2008(data=__createChannel(record))


def get_channels(ecosystem_id):  # noqa: E501
    """get the channels of an ecosystem

     # noqa: E501

    :param ecosystem_id: ecosystem
    :type ecosystem_id: int

    :rtype: InlineResponse2007
    """
    with database.session_scope() as session:
        return InlineResponse2007(
            data=[__createChannel(record) for record in
                  session.query(database.Channel).filter_by(ecosystem_id=ecosystem_id).all()]
        )
