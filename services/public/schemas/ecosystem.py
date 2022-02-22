from public.jsonapi import attributes, data, item, item_list, create_relationships, Link, DataList
from pydantic import BaseModel, Field
from typing import List, Optional


class GitCredential(BaseModel):
    url: str = ""
    username: Optional[str]
    password: Optional[str]


@attributes
class EcosystemWrite(BaseModel):
    name: str = ""
    user: Optional[str]
    conan_remote: Optional[str]
    conan_config_url: Optional[str]
    conan_config_path: Optional[str]
    conan_user: Optional[str]
    conan_password: Optional[str]
    credentials: List[GitCredential] = Field(default_factory=list, alias="credential_values")
    known_hosts: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "name": "My Company",
                "user": "mycompany",
                "conan_remote": "uboot",
                "conan_config_url": "git@github.com:uboot/conan-config.git",
                "conan_config_path": "conan-config",
                "conan_config_branch": "master",
                "conan_user": "agent",
                "conan_password": "Passw0rd",
                "credentials": [{
                    "url": "https://user@github.com",
                    "username": "user",
                    "password": "Passw0rd"
                }],
                "known_hosts": "Z2l0aHViLmNvbSwxNDAuODIuMTIxLjQgc3NoLXJzYSBBQUFBQjNOemFDMXljMkVBQUFBQkl3QUFBUUVBcTJBN2h"
                               "SR21kbm05dFVEYk85SURTd0JLNlRiUWErUFhZUENQeTZyYlRyVHR3N1BIa2NjS3JwcDB5VmhwNUhkRUljS3I2cE"
                               "xsVkRCZk9MWDlRVXN5Q09WMHd6ZmpJSk5sR0VZc2RsTEppekhoYm4ybVVqdlNBSFFxWkVUWVA4MWVGekxRTm5QS"
                               "HQ0RVZWVWg3VmZERVNVODRLZXptRDVRbFdwWExtdlUzMS95TWYrU2U4eGhIVHZLU0NaSUZJbVd3b0c2bWJVb1dm"
                               "OW56cElvYVNqQit3ZXFxVVVtcGFhYXNYVmFsNzJKK1VYMkIrMlJQVzNSY1QwZU96UWdxbEpMM1JLclRKdmRzakU"
                               "zSkVBdkdxM2xHSFNaWHkyOEczc2t1YTJTbVZpL3c0eUNFNmdiT0RxblRXbGc3K3dDNjA0eWRHWEE4VkppUzVhcD"
                               "QzSlhpVUZGQWFRPT0K"
            }
        }


@attributes
class EcosystemRead(EcosystemWrite):
    public_ssh_key: str

    class Config:
        schema_extra = {
            "example": {
                "public_ssh_key": "",
                **EcosystemWrite.Config.schema_extra["example"]
            }
        }


@data
class EcosystemWriteData(BaseModel):
    type: str = "users"
    attributes: EcosystemWrite = Field(default_factory=EcosystemWrite)

    class Config:
        pass


@item
class EcosystemWriteItem(BaseModel):
    data: EcosystemWriteData = Field(default_factory=EcosystemWriteData)

    class Config:
        pass


ecosystem_relationships = create_relationships("EcosystemRelationships", [
    Link("builds", "build"),
    DataList("channels", "channels"),
    DataList("profiles", "profiles"),
    Link("repos", "repo"),
    Link("recipes", "recipe")
])


@data
class EcosystemReadData(BaseModel):
    id: Optional[str]
    type: str = "users"
    attributes: EcosystemRead = Field(default_factory=EcosystemRead)
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
