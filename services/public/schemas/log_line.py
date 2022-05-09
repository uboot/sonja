from datetime import datetime
from public.jsonapi import attributes, data, item, item_list, create_relationships, DataItem, PagedItemListMeta
from pydantic import BaseModel, Field
from typing import Optional, List


@attributes
class LogLine(BaseModel):
    number: int
    time: datetime
    content: str

    class Config:
        schema_extra = {
            "example": {
                "number": "10",
                "time": "2000-01-02T13:30:00",
                "content": "Start build..."
            }
        }


@data
class LogLineReadData(BaseModel):
    id: Optional[str]
    type: str = "log-lines"
    attributes: LogLine = Field(default_factory=LogLine)

    class Config:
        pass


@item
class LogLineReadItem(BaseModel):
    data: LogLineReadData = Field(default_factory=LogLineReadData)

    class Config:
        pass


@item_list
class LogLineReadList(BaseModel):
    data: List[LogLineReadData] = Field(default_factory=list)
    meta: Optional[PagedItemListMeta]

    class Config:
        pass
