from public.jsonapi import attributes, data, item, item_list, create_relationships, Link, DataItem, DataList
from pydantic import BaseModel, Field
from typing import List, Optional


@attributes
class Recipe(BaseModel):
    name: str = ""
    version: str
    user: Optional[str]
    channel: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "name": "hello",
                "version": "1.2.3",
                "user": "sonja",
                "channel": "stable"
            }
        }


recipe_relationships = create_relationships("RecipeRelationships", [
    DataItem("ecosystem", "ecosystems"),
    DataList("required_by", "builds"),
    Link("revisions", "revision")
])


@data
class RecipeReadData(BaseModel):
    id: Optional[str]
    type: str = "recipes"
    attributes: Recipe = Field(default_factory=Recipe)
    relationships: recipe_relationships = Field(default_factory=recipe_relationships)

    class Config:
        pass


@item
class RecipeReadItem(BaseModel):
    data: RecipeReadData = Field(default_factory=RecipeReadData)

    class Config:
        pass


@item_list
class RecipeReadList(BaseModel):
    data: List[RecipeReadData] = Field(default_factory=list)

    class Config:
        pass


@attributes
class RecipeRevision(BaseModel):
    revision: str = ""

    class Config:
        schema_extra = {
            "example": {
                "revision": "08979da6c039dd919292f7408785e2ad711b2fd5"
            }
        }


recipe_revision_relationships = create_relationships("RecipeRevisionRelationships", [
    DataItem("recipe", "recipes"),
    DataList("packages", "packages")
])


@data
class RecipeRevisionReadData(BaseModel):
    id: Optional[str]
    type: str = "recipe-revisions"
    attributes: RecipeRevision = Field(default_factory=RecipeRevision)
    relationships: recipe_revision_relationships = Field(default_factory=recipe_revision_relationships)

    class Config:
        pass


@item
class RecipeRevisionReadItem(BaseModel):
    data: RecipeRevisionReadData = Field(default_factory=RecipeRevisionReadData)

    class Config:
        pass


@item_list
class RecipeRevisionReadList(BaseModel):
    data: List[RecipeRevisionReadData] = Field(default_factory=list)

    class Config:
        pass
