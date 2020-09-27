# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.setting import Setting  # noqa: F401,E501
from swagger_server import util


class Profile(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, id: int=None, name: str=None, container: str=None, settings: List[Setting]=None):  # noqa: E501
        """Profile - a model defined in Swagger

        :param id: The id of this Profile.  # noqa: E501
        :type id: int
        :param name: The name of this Profile.  # noqa: E501
        :type name: str
        :param container: The container of this Profile.  # noqa: E501
        :type container: str
        :param settings: The settings of this Profile.  # noqa: E501
        :type settings: List[Setting]
        """
        self.swagger_types = {
            'id': int,
            'name': str,
            'container': str,
            'settings': List[Setting]
        }

        self.attribute_map = {
            'id': 'id',
            'name': 'name',
            'container': 'container',
            'settings': 'settings'
        }
        self._id = id
        self._name = name
        self._container = container
        self._settings = settings

    @classmethod
    def from_dict(cls, dikt) -> 'Profile':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Profile of this Profile.  # noqa: E501
        :rtype: Profile
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self) -> int:
        """Gets the id of this Profile.


        :return: The id of this Profile.
        :rtype: int
        """
        return self._id

    @id.setter
    def id(self, id: int):
        """Sets the id of this Profile.


        :param id: The id of this Profile.
        :type id: int
        """

        self._id = id

    @property
    def name(self) -> str:
        """Gets the name of this Profile.


        :return: The name of this Profile.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name: str):
        """Sets the name of this Profile.


        :param name: The name of this Profile.
        :type name: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def container(self) -> str:
        """Gets the container of this Profile.


        :return: The container of this Profile.
        :rtype: str
        """
        return self._container

    @container.setter
    def container(self, container: str):
        """Sets the container of this Profile.


        :param container: The container of this Profile.
        :type container: str
        """
        if container is None:
            raise ValueError("Invalid value for `container`, must not be `None`")  # noqa: E501

        self._container = container

    @property
    def settings(self) -> List[Setting]:
        """Gets the settings of this Profile.


        :return: The settings of this Profile.
        :rtype: List[Setting]
        """
        return self._settings

    @settings.setter
    def settings(self, settings: List[Setting]):
        """Sets the settings of this Profile.


        :param settings: The settings of this Profile.
        :type settings: List[Setting]
        """

        self._settings = settings
