from public.jsonapi import attributes, data, item, item_list, create_relationships, Link, DataItem
from public.schemas.profile import Label
from pydantic import BaseModel, Field
from typing import List, Optional


class Option(BaseModel):
    key: str = ""
    value: str = ""


@attributes
class Repo(BaseModel):
    name: str = ""
    url: Optional[str]
    path: Optional[str]
    version: Optional[str]
    exclude: List[Label] = Field(default_factory=list, alias="exclude_values")
    options: List[Option] = Field(default_factory=list, alias="options_values")

    class Config:
        schema_extra = {
            "example": {
                "name": "Hello",
                "url": "https://github.com/uboot/sonja.git",
                "path": "packages/hello",
                "version": "1.2.3",
                "exclude": [{
                    "label": "embedded"
                }],
                "options": [{
                    "key": "hello:shared",
                    "value": "True"
                }]
            }
        }


repo_write_relationships = create_relationships("RepoWriteRelationships", [
    DataItem("ecosystem", "ecosystems")
])


@data
class RepoWriteData(BaseModel):
    type: str = "repos"
    attributes: Repo = Field(default_factory=Repo)
    relationships: repo_write_relationships = Field(default_factory=repo_write_relationships)

    class Config:
        pass


@item
class RepoWriteItem(BaseModel):
    data: RepoWriteData = Field(default_factory=RepoWriteData)

    class Config:
        pass


repo_read_relationships = create_relationships("RepoReadRelationships", [
    DataItem("ecosystem", "ecosystems"),
    Link("commits", "commit")
])


@data
class RepoReadData(BaseModel):
    id: Optional[str]
    type: str = "repos"
    attributes: Repo = Field(default_factory=Repo)
    relationships: repo_read_relationships = Field(default_factory=repo_read_relationships)

    class Config:
        pass


@item
class RepoReadItem(BaseModel):
    data: RepoReadData = Field(default_factory=RepoReadData)

    class Config:
        pass


@item_list
class RepoReadList(BaseModel):
    data: List[RepoReadData] = Field(default_factory=list)

    class Config:
        pass
