from enum import Enum
from public.jsonapi import attributes, data, item, item_list, create_relationships, DataItem, DataList
from pydantic import BaseModel, Field
from typing import List, Optional


class StatusEnum(str, Enum):
    active = "active"
    error = "error"
    new = "new"
    stopped = "stopped"
    stopping = "stopping"
    success = "success"


@attributes
class Build(BaseModel):
    status: StatusEnum = Field(alias="status_value")

    class Config:
        schema_extra = {
            "example": {
                "status": "new"
            }
        }


build_relationships = create_relationships("BuildRelationships", [
    DataItem("ecosystem", "ecosystems"),
    DataItem("commit", "commits"),
    DataItem("profile", "profiles"),
    DataItem("log", "logs"),
    DataItem("package", "packages"),
    DataList("missing_packages", "packages"),
    DataList("missing_recipes", "recipes")
])


@data
class BuildWriteData(BaseModel):
    type: str = "builds"
    attributes: Build = Field(default_factory=Build)

    class Config:
        pass


@item
class BuildWriteItem(BaseModel):
    data: BuildWriteData = Field(default_factory=BuildWriteData)

    class Config:
        pass


@data
class BuildReadData(BaseModel):
    id: Optional[str]
    type: str = "builds"
    attributes: Build = Field(default_factory=Build)
    relationships: build_relationships = Field(default_factory=build_relationships)

    class Config:
        pass


@item
class BuildReadItem(BaseModel):
    data: BuildReadData = Field(default_factory=BuildReadData)

    class Config:
        pass


@item_list
class BuildReadList(BaseModel):
    data: List[BuildReadData] = Field(default_factory=list)

    class Config:
        pass
