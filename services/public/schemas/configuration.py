from public.jsonapi import attributes, data, item, item_list
from pydantic import BaseModel, Field
from typing import Optional


@attributes
class Configuration(BaseModel):
    github_secret: str

    class Config:
        schema_extra = {
            "example": {
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
