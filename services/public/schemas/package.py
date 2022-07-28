from public.jsonapi import attributes, data, item, item_list, create_relationships, Link, DataItem, DataList
from pydantic import BaseModel, Field
from typing import Optional


@attributes
class Package(BaseModel):
    package_id: str

    class Config:
        schema_extra = {
            "example": {
                "package_id": "cda61897af86d277c61b93fa40c92da744abdf33"
            }
        }


package_relationships = create_relationships("PackageRelationships", [
    DataItem("recipe_revision", "recipe-revisions"),
    DataList("builds", "builds"),
    DataList("requires", "packages"),
    DataList("required_by", "packages"),
])


@data
class PackageReadData(BaseModel):
    id: Optional[str]
    type: str = "packages"
    attributes: Package = Field(default_factory=Package)
    relationships: package_relationships = Field(default_factory=package_relationships)

    class Config:
        pass


@item
class PackageReadItem(BaseModel):
    data: PackageReadData = Field(default_factory=PackageReadData)

    class Config:
        pass
