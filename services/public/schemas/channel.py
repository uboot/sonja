from public.jsonapi import attributes, data, item, item_list, create_relationships, Link, DataItem
from pydantic import BaseModel, Field
from typing import List, Optional


class Option(BaseModel):
    key: str = ""
    value: str = ""


@attributes
class Channel(BaseModel):
    name: str = ""
    conan_channel: Optional[str]
    ref_pattern: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "name": "Releases",
                "conan_channel": "stable",
                "ref_pattern": "main"
            }
        }


channel_relationships = create_relationships("ChannelRelationships", [
    DataItem("ecosystem", "ecosystems")
])


@data
class ChannelWriteData(BaseModel):
    type: str = "channels"
    attributes: Channel = Field(default_factory=Channel)
    relationships: channel_relationships = Field(default_factory=channel_relationships)

    class Config:
        pass


@item
class ChannelWriteItem(BaseModel):
    data: ChannelWriteData = Field(default_factory=ChannelWriteData)

    class Config:
        pass


channel_read_relationships = create_relationships("ChannelReadRelationships", [
    DataItem("ecosystem", "ecosystems"),
    Link("commits", "commit")
])


@data
class ChannelReadData(BaseModel):
    id: Optional[str]
    type: str = "channels"
    attributes: Channel = Field(default_factory=Channel)
    relationships: channel_relationships = Field(default_factory=channel_relationships)

    class Config:
        pass


@item
class ChannelReadItem(BaseModel):
    data: ChannelReadData = Field(default_factory=ChannelReadData)

    class Config:
        pass
