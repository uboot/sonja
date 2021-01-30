# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class EcosystemRelationshipsProfilesData(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, type: str=None, id: str=None):  # noqa: E501
        """EcosystemRelationshipsProfilesData - a model defined in Swagger

        :param type: The type of this EcosystemRelationshipsProfilesData.  # noqa: E501
        :type type: str
        :param id: The id of this EcosystemRelationshipsProfilesData.  # noqa: E501
        :type id: str
        """
        self.swagger_types = {
            'type': str,
            'id': str
        }

        self.attribute_map = {
            'type': 'type',
            'id': 'id'
        }
        self._type = type
        self._id = id

    @classmethod
    def from_dict(cls, dikt) -> 'EcosystemRelationshipsProfilesData':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Ecosystem_relationships_profiles_data of this EcosystemRelationshipsProfilesData.  # noqa: E501
        :rtype: EcosystemRelationshipsProfilesData
        """
        return util.deserialize_model(dikt, cls)

    @property
    def type(self) -> str:
        """Gets the type of this EcosystemRelationshipsProfilesData.


        :return: The type of this EcosystemRelationshipsProfilesData.
        :rtype: str
        """
        return self._type

    @type.setter
    def type(self, type: str):
        """Sets the type of this EcosystemRelationshipsProfilesData.


        :param type: The type of this EcosystemRelationshipsProfilesData.
        :type type: str
        """

        self._type = type

    @property
    def id(self) -> str:
        """Gets the id of this EcosystemRelationshipsProfilesData.


        :return: The id of this EcosystemRelationshipsProfilesData.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id: str):
        """Sets the id of this EcosystemRelationshipsProfilesData.


        :param id: The id of this EcosystemRelationshipsProfilesData.
        :type id: str
        """

        self._id = id
