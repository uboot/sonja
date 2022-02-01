from dataclasses import dataclass, field, fields
from pydantic import BaseModel
from pydantic.fields import ModelField
from types import MethodType
from typing import get_origin, get_args, List, Optional, Type


def attributes(cls: Type):
    cls.Config.orm_mode = True
    cls.Config.allow_population_by_field_name = True
    return cls


def data(cls: Type):
    example = dict()
    example["id"] = "1"
    example["type"] = cls.__fields__['type'].default
    example["attributes"] = cls.__fields__['attributes'].type_.Config.schema_extra["example"]
    setattr(cls.Config, "schema_extra", dict())
    cls.Config.schema_extra["example"] = example
    return cls


def item(cls: Type):
    @staticmethod
    def create_obj(obj: object):
        values = {
            "data": {
                "id": obj.id,
                "type": cls.__fields__["data"].type_.__fields__["type"].default,
                "attributes": obj
            }
        }

        return cls(**values)

    setattr(cls, "from_db", create_obj)

    example = dict()
    example["data"] = cls.__fields__['data'].type_.Config.schema_extra["example"]
    setattr(cls.Config, "schema_extra", dict())
    cls.Config.schema_extra["example"] = example

    return cls


def item_list(cls: Type):
    @staticmethod
    def create_obj(objs: list):

        values = {
            "data": [{
                "id": obj.id,
                "type": cls.__fields__["data"].type_.__fields__["type"].default,
                "attributes": obj
            }] for obj in objs
        }

        return cls(**values)

    setattr(cls, "from_db", create_obj)

    example = dict()
    example["data"] = [cls.__fields__['data'].type_.Config.schema_extra["example"]]
    setattr(cls.Config, "schema_extra", dict())
    cls.Config.schema_extra["example"] = example

    return cls
