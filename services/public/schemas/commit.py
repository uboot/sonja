from public.jsonapi import attributes, data, item, item_list, create_relationships, Link, DataItem, DataList
from pydantic import BaseModel, Field
from typing import List, Optional


@attributes
class Commit(BaseModel):
    sha: str
    message: str
    user_name: str
    user_email: str

    class Config:
        schema_extra = {
            "example": {
                "sha": "a37dc82e296d55c23f738b79f139e627920c",
                "message": "Initial commit",
                "user_name": "Joe Smith",
                "user_email": "joe.smith@acme.com"
            }
        }


commit_relationships = create_relationships("CommitRelationships", [
    DataItem("repo", "repos"),
    DataItem("channel", "channels"),
    DataList("builds", "builds"),
])


@data
class CommitReadData(BaseModel):
    id: Optional[str]
    type: str = "commits"
    attributes: Commit = Field(default_factory=Commit)
    relationships: commit_relationships = Field(default_factory=commit_relationships)

    class Config:
        pass


@item
class CommitReadItem(BaseModel):
    data: CommitReadData = Field(default_factory=CommitReadData)

    class Config:
        pass


@item_list
class CommitReadList(BaseModel):
    data: List[CommitReadData] = Field(default_factory=list)

    class Config:
        pass
