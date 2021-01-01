# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.commit import Commit  # noqa: F401,E501
from swagger_server import util


class InlineResponse2005(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, data: List[Commit]=None):  # noqa: E501
        """InlineResponse2005 - a model defined in Swagger

        :param data: The data of this InlineResponse2005.  # noqa: E501
        :type data: List[Commit]
        """
        self.swagger_types = {
            'data': List[Commit]
        }

        self.attribute_map = {
            'data': 'data'
        }
        self._data = data

    @classmethod
    def from_dict(cls, dikt) -> 'InlineResponse2005':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The inline_response_200_5 of this InlineResponse2005.  # noqa: E501
        :rtype: InlineResponse2005
        """
        return util.deserialize_model(dikt, cls)

    @property
    def data(self) -> List[Commit]:
        """Gets the data of this InlineResponse2005.


        :return: The data of this InlineResponse2005.
        :rtype: List[Commit]
        """
        return self._data

    @data.setter
    def data(self, data: List[Commit]):
        """Sets the data of this InlineResponse2005.


        :param data: The data of this InlineResponse2005.
        :type data: List[Commit]
        """

        self._data = data