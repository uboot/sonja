from public.jsonapi import attributes, data, item, item_list, create_relationships, Link, DataItem, DataList
from pydantic import BaseModel, Field
from typing import Optional


@attributes
class Log(BaseModel):
    logs: str

    class Config:
        schema_extra = {
            "example": {
                "logs": "Start build\\nRun Build\\nUpload..."
            }
        }


@data
class LogReadData(BaseModel):
    id: Optional[str]
    type: str = "logs"
    attributes: Log = Field(default_factory=Log)

    class Config:
        pass


@item
class LogReadItem(BaseModel):
    data: LogReadData = Field(default_factory=LogReadData)

    class Config:
        pass
