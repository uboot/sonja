from datetime import datetime
from enum import Enum
from public.jsonapi import attributes, data, item, item_list, create_relationships, DataItem
from pydantic import BaseModel, Field
from typing import Optional, List


class StatusEnum(str, Enum):
    active = "active"
    error = "error"
    stopped = "stopped"
    success = "success"
    stalled = "stalled"


@attributes
class Run(BaseModel):
    status: StatusEnum = Field(alias="status_value")
    started: datetime

    class Config:
        schema_extra = {
            "example": {
                "status": "new",
                "started": "2000-01-02T13:30:00"
            }
        }


run_relationships = create_relationships("RunRelationships", [
    DataItem("build", "builds")
])


@data
class RunReadData(BaseModel):
    id: Optional[str]
    type: str = "runs"
    attributes: Run = Field(default_factory=Run)
    relationships: run_relationships = Field(default_factory=run_relationships)

    class Config:
        pass


@item
class RunReadItem(BaseModel):
    data: RunReadData = Field(default_factory=RunReadData)

    class Config:
        pass


@item_list
class RunReadList(BaseModel):
    data: List[RunReadData] = Field(default_factory=list)

    class Config:
        pass

