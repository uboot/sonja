# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.repo import Repo  # noqa: F401,E501
from swagger_server import util


class InlineResponse2002(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, data: Repo=None):  # noqa: E501
        """InlineResponse2002 - a model defined in Swagger

        :param data: The data of this InlineResponse2002.  # noqa: E501
        :type data: Repo
        """
        self.swagger_types = {
            'data': Repo
        }

        self.attribute_map = {
            'data': 'data'
        }
        self._data = data

    @classmethod
    def from_dict(cls, dikt) -> 'InlineResponse2002':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The inline_response_200_2 of this InlineResponse2002.  # noqa: E501
        :rtype: InlineResponse2002
        """
        return util.deserialize_model(dikt, cls)

    @property
    def data(self) -> Repo:
        """Gets the data of this InlineResponse2002.


        :return: The data of this InlineResponse2002.
        :rtype: Repo
        """
        return self._data

    @data.setter
    def data(self, data: Repo):
        """Sets the data of this InlineResponse2002.


        :param data: The data of this InlineResponse2002.
        :type data: Repo
        """

        self._data = data