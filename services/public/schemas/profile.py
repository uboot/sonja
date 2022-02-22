from enum import Enum
from public.jsonapi import attributes, data, item, item_list, create_relationships, Link, DataItem
from pydantic import BaseModel, Field
from typing import List, Optional


class PlatformEnum(str, Enum):
    linux = "linux"
    windows = "windows"


class Label(BaseModel):
    label: str = ""


@attributes
class Profile(BaseModel):
    name: str = ""
    container: Optional[str]
    docker_user: Optional[str]
    docker_password: Optional[str]
    platform: Optional[PlatformEnum] = Field(alias="platform_value")
    conan_profile: Optional[str]
    labels: List[Label] = Field(default_factory=list, alias="labels_value")

    class Config:
        schema_extra = {
            "example": {
                "name": "GCC 9",
                "container": "uboot/gcc9:latest",
                "docker_user": "user",
                "docker_password": "paSSw0rd",
                "platform": "linux",
                "conan_profile": "linux-debug",
                "labels": [{
                    "label": "embedded"
                }]
            }
        }


profile_relationships = create_relationships("ProfileRelationships", [
    DataItem("ecosystem", "ecosystems")
])


@data
class ProfileWriteData(BaseModel):
    type: str = "users"
    attributes: Profile = Field(default_factory=Profile)
    relationships: profile_relationships = Field(default_factory=profile_relationships)

    class Config:
        pass


@item
class ProfileWriteItem(BaseModel):
    data: ProfileWriteData = Field(default_factory=ProfileWriteData)

    class Config:
        pass


@data
class ProfileReadData(BaseModel):
    id: Optional[str]
    type: str = "users"
    attributes: Profile = Field(default_factory=Profile)
    relationships: profile_relationships = Field(default_factory=profile_relationships)

    class Config:
        pass


@item
class ProfileReadItem(BaseModel):
    data: ProfileReadData = Field(default_factory=ProfileReadData)

    class Config:
        pass
