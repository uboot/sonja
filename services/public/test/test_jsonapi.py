from public.jsonapi import attributes, create_relationships, DataItem, DataList, data, item, item_list, Link
from pydantic import BaseModel, Field
from typing import List, Optional
import unittest


@attributes
class User(BaseModel):
    user_id: str = ""
    name: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "user_id": "joe",
                "name": "Joe Doe",
            }
        }


user_relationships = create_relationships("UserRelationships", [
    DataItem("company", "companies"),
    DataList("hobbies", "hobbies"),
    Link("friends", "friends")
])


@data
class UserData(BaseModel):
    id: Optional[str]
    type: str = "users"
    attributes: User = Field(default_factory=User)
    relationships: user_relationships = Field(default_factory=user_relationships)

    class Config:
        pass


@item
class UserItem(BaseModel):
    data: UserData = Field(default_factory=UserData)

    class Config:
        pass


@item_list
class UserList(BaseModel):
    data: List[UserData] = Field(default_factory=list)

    class Config:
        pass


class CompanyModel:
    id = 1


class HobbyModel:
    def __init__(self, id):
        self.id = id


class UserModel:
    def __init__(self, id_, user_id, name, company, hobbies):
        self.id = id_
        self.user_id = user_id
        self.name = name
        self.company = company
        self.hobbies = hobbies


class TestJsonapi(unittest.TestCase):
    def test_attributes(self):
        self.assertDictEqual({'user_id': '', 'name': None}, User().dict())
        self.assertDictEqual({'user_id': 'joe', 'name': 'Joe Doe'}, User.Config.schema_extra["example"])

    def test_data(self):
        self.assertDictEqual({'attributes': {'user_id': '', 'name': None}, 'id': None, 'type': 'users',
                              'relationships': {'company': {'data': {'id': '', 'type': 'companies'}},
                                                'hobbies': {'data': []},
                                                'friends': {'links': {'related': 'friends'}}}},
                             UserData().dict())
        self.assertDictEqual({'attributes': {'user_id': 'joe', 'name': 'Joe Doe'}, 'id': '1', 'type': 'users',
                              'relationships': {'company': {'data': {'id': '1', 'type': 'companies'}},
                                                'friends': {'links': {'related': 'friends'}},
                                                'hobbies': {'data': [{'id': '1', 'type': 'hobbies'}]}}},
                             UserData.Config.schema_extra["example"])

    def test_item(self):
        self.assertDictEqual({'data': {'id': None, 'type': 'users', 'attributes': {'user_id': '', 'name': None},
                                       'relationships': {'company': {'data': {'id': '', 'type': 'companies'}},
                                                         'hobbies': {'data': []},
                                                         'friends': {'links': {'related': 'friends'}}}}},
                             UserItem().dict())
        self.assertDictEqual({'data': {'attributes': {'user_id': 'joe', 'name': 'Joe Doe'}, 'id': '1', 'type': 'users',
                                       'relationships': {'company': {'data': {'id': '1', 'type': 'companies'}},
                                                         'friends': {'links': {'related': 'friends'}},
                                                         'hobbies': {'data': [{'id': '1', 'type': 'hobbies'}]}}}},
                             UserItem().Config.schema_extra["example"])

    def test_item_list(self):
        self.assertDictEqual({'data': []},
                             UserList().dict())
        self.assertDictEqual({'data': [{'attributes': {'user_id': 'joe', 'name': 'Joe Doe'}, 'id': '1', 'type': 'users',
                                        'relationships': {'company': {'data': {'id': '1', 'type': 'companies'}},
                                                          'friends': {'links': {'related': 'friends'}},
                                                          'hobbies': {'data': [{'id': '1', 'type': 'hobbies'}]}} }]},
                             UserList().Config.schema_extra["example"])

    def test_item_from_db(self):
        user_model = UserModel(id_ = 2, user_id = "user", name = "Joe", company = CompanyModel(),
                               hobbies = [HobbyModel(3), HobbyModel(4)])
        user_item = UserItem.from_db(user_model)
        self.assertDictEqual({'data': {'attributes': {'name': 'Joe', 'user_id': 'user'}, 'id': '2', 'type': 'users',
                                       'relationships': {'company': {'data': {'id': '1', 'type': 'companies'}},
                                                         'friends': {'links': {'related': 'friends'}},
                                                         'hobbies': {'data': [{'id': '3', 'type': 'hobbies'},
                                                                              {'id': '4', 'type': 'hobbies'}]}
                                                         }}}, user_item.dict())

    def test_list_from_db(self):
        user_model = UserModel(id_ = 2, user_id = "user", name = "Joe", company = CompanyModel(),
                               hobbies = [HobbyModel(3), HobbyModel(4)])
        user_list = UserList.from_db([user_model])
        self.assertDictEqual({'data': [{'attributes': {'name': 'Joe', 'user_id': 'user'}, 'id': '2', 'type': 'users',
                                        'relationships': {'company': {'data': {'id': '1', 'type': 'companies'}},
                                                          'friends': {'links': {'related': 'friends'}},
                                                          'hobbies': {'data': [{'id': '3', 'type': 'hobbies'},
                                                                               {'id': '4', 'type': 'hobbies'}]}
                                                         }}]}, user_list.dict())
