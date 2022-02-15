from pydantic import create_model
from typing import List, Type, Union


def attributes(cls: Type):
    cls.Config.orm_mode = True
    cls.Config.allow_population_by_field_name = True
    return cls


def data(cls: Type):
    example = dict()
    example["id"] = "1"
    example["type"] = cls.__fields__["type"].default
    example["attributes"] = cls.__fields__["attributes"].type_.Config.schema_extra["example"]
    if "relationships" in cls.__fields__:
        example["relationships"] = {
            f.name: f.type_.Config.schema_extra["example"] for f in cls.__fields__["relationships"].type_.__fields__.values()
        }
    setattr(cls.Config, "schema_extra", dict())
    cls.Config.schema_extra["example"] = example
    return cls


def _create_data_obj(cls: Type, obj: object):
    data_obj = {
        "id": obj.id,
        "type": cls.__fields__["data"].type_.__fields__["type"].default,
        "attributes": obj
    }

    if "relationships" in cls.__fields__["data"].type_.__fields__:
        fields = cls.__fields__["data"].type_.__fields__["relationships"].type_.__fields__
        relationships = {
            fields[f].name: fields[f].type_.from_db(obj) for f in fields
        }
        data_obj["relationships"] = relationships

    return data_obj


def item(cls: Type):
    @staticmethod
    def from_db(obj: object):
        values = {
            "data": _create_data_obj(cls, obj)
        }

        return cls(**values)

    setattr(cls, "from_db", from_db)

    example = dict()
    example["data"] = cls.__fields__['data'].type_.Config.schema_extra["example"]
    setattr(cls.Config, "schema_extra", dict())
    cls.Config.schema_extra["example"] = example

    return cls


def item_list(cls: Type):
    @staticmethod
    def from_db(objs: list):

        values = {
            "data": [_create_data_obj(cls, obj) for obj in objs]
        }

        return cls(**values)

    setattr(cls, "from_db", from_db)

    example = dict()
    example["data"] = [cls.__fields__['data'].type_.Config.schema_extra["example"]]
    setattr(cls.Config, "schema_extra", dict())
    cls.Config.schema_extra["example"] = example

    return cls


class Link:
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

    def create_model(self, parent_name: str):
        config_class = type("Config", (object,), {
            "schema_extra": {
                "example": {
                    "links": {
                        "related": self.url
                    }
                }
            }
        })
        related = create_model(f"{parent_name}{self.name.capitalize()}Related", related=(str, self.url))
        model = create_model(f"{parent_name}{self.name.capitalize()}Link", links=(related, related()),
                             __config__=config_class)

        @staticmethod
        def from_db(obj: object):
            return model().dict()

        setattr(model, "from_db", from_db)
        return model


class DataItem:
    def __init__(self, name: str, type_: str):
        self.name = name
        self.type_ = type_

    def create_model(self, parent_name: str):
        config_class = type("Config", (object,), {
            "schema_extra": {
                "example": {
                    "data": {
                        "id": "1",
                        "type": self.type_
                    }
                }
            }
        })
        data_item = create_model(f"{parent_name}{self.name.capitalize()}Item", type=(str, self.type_), id=(str, ""))
        model = create_model(f"{parent_name}{self.name.capitalize()}Data", data=(data_item, data_item()),
                             __config__=config_class)

        @staticmethod
        def from_db(obj: object):
            return {"data": {"id": getattr(obj, self.name).id, "type": self.type_}}

        setattr(model, "from_db", from_db)
        return model


class DataList:
    def __init__(self, name: str, type_: str):
        self.name = name
        self.type_ = type_

    def create_model(self, parent_name: str):
        config_class = type("Config", (object,), {
            "schema_extra": {
                "example": {
                    "data": [{
                        "id": "1",
                        "type": self.type_
                    }]
                }
            }
        })
        data_item = create_model(f"{parent_name}{self.name.capitalize()}Item", type=(str, self.type_), id=(str, ...))
        model = create_model(f"{parent_name}{self.name.capitalize()}Data", data=(List[data_item], []),
                             __config__=config_class)

        @staticmethod
        def from_db(obj: object):
            return {"data": [{"id": o.id, "type": self.type_} for o in getattr(obj, self.name)]}

        setattr(model, "from_db", from_db)
        return model


def create_relationships(name: str, relationships: List[Union[Link, DataItem, DataList]]):
    models = {r.name: r.create_model(name) for r in relationships}
    items = {
        m: (models[m], models[m]()) for m in models
    }
    return create_model(name, **items)
