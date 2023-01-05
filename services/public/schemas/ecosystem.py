from public.jsonapi import attributes, data, item, item_list, create_relationships, Link, DataList
from pydantic import BaseModel, Field
from typing import List, Optional


class ConanCredential(BaseModel):
    remote: Optional[str]
    username: Optional[str]
    password: Optional[str]


@attributes
class Ecosystem(BaseModel):
    name: str = ""
    user: Optional[str]
    conan_remote: Optional[str]
    conan_config_url: Optional[str]
    conan_config_path: Optional[str]
    conan_config_branch: Optional[str]
    conan_credentials: List[ConanCredential] = Field(default_factory=list, alias="conan_credential_values")

    class Config:
        schema_extra = {
            "example": {
                "name": "My Company",
                "user": "mycompany",
                "conan_config_url": "git@github.com:uboot/conan-config.git",
                "conan_config_path": "default",
                "conan_config_branch": "master",
                "conan_credentials": [{
                    "remote": "uboot",
                    "username": "agent",
                    "password": "Passw0rd"
                }],
            }
        }


@data
class EcosystemWriteData(BaseModel):
    type: str = "ecosystems"
    attributes: Ecosystem = Field(default_factory=Ecosystem)

    class Config:
        pass


@item
class EcosystemWriteItem(BaseModel):
    data: EcosystemWriteData = Field(default_factory=EcosystemWriteData)

    class Config:
        pass


ecosystem_relationships = create_relationships("EcosystemRelationships", [
    DataList("channels", "channels"),
    DataList("profiles", "profiles"),
    Link("repos", "repo"),
    Link("recipes", "recipe")
])


@data
class EcosystemReadData(BaseModel):
    id: Optional[str]
    type: str = "ecosystems"
    attributes: Ecosystem = Field(default_factory=Ecosystem)
    relationships: ecosystem_relationships = Field(default_factory=ecosystem_relationships)

    class Config:
        pass


@item
class EcosystemReadItem(BaseModel):
    data: EcosystemReadData = Field(default_factory=EcosystemReadData)

    class Config:
        pass


@item_list
class EcosystemReadList(BaseModel):
    data: List[EcosystemReadData] = Field(default_factory=list)

    class Config:
        pass
