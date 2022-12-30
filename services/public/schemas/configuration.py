from public.jsonapi import attributes, data, item, item_list
from pydantic import BaseModel, Field
from typing import List, Optional


class GitCredential(BaseModel):
    url: str = ""
    username: Optional[str]
    password: Optional[str]


class DockerCredential(BaseModel):
    server: Optional[str]
    username: Optional[str]
    password: Optional[str]


@attributes
class Configuration(BaseModel):
    public_ssh_key: Optional[str]
    git_credentials: List[GitCredential] = Field(default_factory=list, alias="git_credential_values")
    docker_credentials: List[DockerCredential] = Field(default_factory=list, alias="docker_credential_values")
    known_hosts: Optional[str]
    github_secret: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "public_ssh_key": "c3NoLXJzYSBBQUFBQjNOemFDMXljMkVBQUFBREFRQUJBQUFDQVFDdzJzUzRTb2FrRVNOMk11M3krc0htQy9I"
                                  "Q3lZOGF6TXhBanNEbjZtSVdvTUFtUHFiMkpDWUFGajRwT09aRllSUm5BaVdWZWtYVTFpR1NJNm9lblZKMTdk"
                                  "YlBtSHEyTDhuZ0NSZy96dDR3L29sMkxuQjFmVkc3YjZEYXdWc05YREljWFhPRHRGT0pEYlo5ZWNiSWlXVERP"
                                  "QlVqTm9VSkNsUFU0N2o2MGNuT2pOTnQxSGhSTis0QVAzUE9JWWRXSE5QVVAxbTA0MktUWlNCRDBBYm9BbEh5"
                                  "VHZqTTAweWtwSkZuNStiZlF5V2ppOFUyOFBRZTFqUWllaEJ5WnhBdjI2L2VkbXppMHZiUUI1YjQ2dmFld0Mz"
                                  "Qjd5U0JNSWF4azZ2WVdWMXVTcERDZmJxdWNaY1RONm1iVmZmNVYxbkF4Q29TZG1BSzZyZ3BhQlorcWFzTmZG"
                                  "c2JrWHZjNWpLbzNsNU5lTDhhb2pvYjNFcFFJT3lCOC9TUis3bTJJbHhFcm5WbGtDT1hJalRXaTNIQ0tNQ3J5"
                                  "dXZ2ajVoSXFoMHd5QktYUjF5OTVpQWxEeXpYNXFwWTZtVWcwalVRa08ybEExbkttQnhraWY0VVpacjZrbDVV"
                                  "QkZPVXh1MzhLc0cwc3FYS1BYNGdRWkNlbVpVdTIwZmdTamJQdm1mYzFmUjJTWHUrUng3SlcvVUxHWlh5dkx1"
                                  "cHdoNlRyMXN4cDl6ek5GSDJTcExUaEpHdlZtY3hFQVlnN1Q1b3BKc09XWkU2TGZKTDQrbzdWVk1vQUFnN0tO"
                                  "ZzU0NHRnNDVEdUFTRDFkRXR0WDZpNk9SLzdtWkJZeWkvZWdNY3NGbzI3elEzN09sblFQV3BvcHFzNlhwTTc0"
                                  "cVExYzIrS0h6anF4U0lIRU9YZzBjeHRYZDJkWlE9PQ==",
                "git_credentials": [{
                    "url": "https://user@github.com",
                    "username": "user",
                    "password": "Passw0rd"
                }],
                "docker_credentials": [{
                    "url": "",
                    "username": "user",
                    "password": "Passw0rd"
                }, {
                    "url": "myregistry.azurecr.io",
                    "username": "myregistry",
                    "password": "Passw0rd"
                }],
                "known_hosts": "Z2l0aHViLmNvbSwxNDAuODIuMTIxLjQgc3NoLXJzYSBBQUFBQjNOemFDMXljMkVBQUFBQkl3QUFBUUVBcTJBN2h"
                               "SR21kbm05dFVEYk85SURTd0JLNlRiUWErUFhZUENQeTZyYlRyVHR3N1BIa2NjS3JwcDB5VmhwNUhkRUljS3I2cE"
                               "xsVkRCZk9MWDlRVXN5Q09WMHd6ZmpJSk5sR0VZc2RsTEppekhoYm4ybVVqdlNBSFFxWkVUWVA4MWVGekxRTm5QS"
                               "HQ0RVZWVWg3VmZERVNVODRLZXptRDVRbFdwWExtdlUzMS95TWYrU2U4eGhIVHZLU0NaSUZJbVd3b0c2bWJVb1dm"
                               "OW56cElvYVNqQit3ZXFxVVVtcGFhYXNYVmFsNzJKK1VYMkIrMlJQVzNSY1QwZU96UWdxbEpMM1JLclRKdmRzakU"
                               "zSkVBdkdxM2xHSFNaWHkyOEczc2t1YTJTbVZpL3c0eUNFNmdiT0RxblRXbGc3K3dDNjA0eWRHWEE4VkppUzVhcD"
                               "QzSlhpVUZGQWFRPT0K",
                "github_secret": "0123467890abcdef0123467890abcdef"
            }
        }


@data
class ConfigurationData(BaseModel):
    id: Optional[str]
    type: str = "configurations"
    attributes: Configuration = Field(default_factory=Configuration)

    class Config:
        pass


@item
class ConfigurationItem(BaseModel):
    data: ConfigurationData = Field(default_factory=ConfigurationData)

    class Config:
        pass
