from enum import Enum
from public.jsonapi import attributes, data, item, item_list
from pydantic import BaseModel, Field
from typing import List, Optional


class PermissionEnum(str, Enum):
    read = "read"
    write = "write"
    admin = "admin"


@attributes
class UserRead(BaseModel):
    permissions: List[PermissionEnum] = Field(default_factory=list, alias="permission_value")
    user_name: str = ""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "user_name": "user",
                "first_name": "Joe",
                "last_name": "Doe",
                "email": "joe.doe@acme.com",
                "permissions": ["read", "write"]
            }
        }


@data
class UserReadData(BaseModel):
    id: Optional[str]
    type: str = "users"
    attributes: UserRead = Field(default_factory=UserRead)

    class Config:
        pass


@item
class UserReadItem(BaseModel):
    data: UserReadData = Field(default_factory=UserReadData)

    class Config:
        pass


@item_list
class UserReadList(BaseModel):
    data: List[UserReadData] = Field(default_factory=list)

    class Config:
        pass


@attributes
class UserWrite(UserRead):
    password: Optional[str] = Field(alias="plain_password")
    old_password: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "password": "pass",
                "old_password": "word",
                **UserRead.Config.schema_extra["example"]
            }
        }


@data
class UserWriteData(BaseModel):
    id: Optional[str]
    type: str = "users"
    attributes: UserWrite = Field(default_factory=UserWrite)

    class Config:
        pass


@item
class UserWriteItem(BaseModel):
    data: UserWriteData = Field(default_factory=UserWriteData)

    class Config:
        pass
