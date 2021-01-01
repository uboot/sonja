# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server.models.channel import Channel  # noqa: F401,E501
from swagger_server import util


class InlineResponse2008(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, data: Channel=None):  # noqa: E501
        """InlineResponse2008 - a model defined in Swagger

        :param data: The data of this InlineResponse2008.  # noqa: E501
        :type data: Channel
        """
        self.swagger_types = {
            'data': Channel
        }

        self.attribute_map = {
            'data': 'data'
        }
        self._data = data

    @classmethod
    def from_dict(cls, dikt) -> 'InlineResponse2008':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The inline_response_200_8 of this InlineResponse2008.  # noqa: E501
        :rtype: InlineResponse2008
        """
        return util.deserialize_model(dikt, cls)

    @property
    def data(self) -> Channel:
        """Gets the data of this InlineResponse2008.


        :return: The data of this InlineResponse2008.
        :rtype: Channel
        """
        return self._data

    @data.setter
    def data(self, data: Channel):
        """Sets the data of this InlineResponse2008.


        :param data: The data of this InlineResponse2008.
        :type data: Channel
        """

        self._data = data