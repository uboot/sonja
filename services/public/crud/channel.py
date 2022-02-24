from public.schemas.channel import ChannelWriteItem
from sonja.database import Ecosystem, Channel, Session
from typing import List


def read_channels(session: Session, ecosystem_id: str) -> List[Channel]:
    return session.query(Channel).filter(Channel.ecosystem_id == ecosystem_id).all()


def read_channel(session: Session, channel_id: str) -> Channel:
    return session.query(Channel).filter(Channel.id == channel_id).first()


def create_channel(session: Session, channel_item: ChannelWriteItem) -> Channel:
    channel = Channel(**channel_item.data.attributes.dict(exclude_unset=True, by_alias=True))
    ecosystem = session.query(Ecosystem).filter(Ecosystem.id == channel_item.data.relationships.ecosystem.data.id).first()
    channel.ecosystem = ecosystem
    session.add(channel)
    session.commit()
    return channel


def update_channel(session: Session, channel: Channel, channel_item: ChannelWriteItem) -> Channel:
    data = channel_item.data.attributes.dict(exclude_unset=True, by_alias=True)
    for attribute in data:
        setattr(channel, attribute, data[attribute])
    session.commit()
    return channel


def delete_channel(session: Session, channel: Channel) -> None:
    session.delete(channel)
