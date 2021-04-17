# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from swagger_server.models.base_model_ import Model
from swagger_server import util


class CommitAttributes(Model):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """
    def __init__(self, sha: str=None, message: str=None, user_name: str=None, user_email: str=None):  # noqa: E501
        """CommitAttributes - a model defined in Swagger

        :param sha: The sha of this CommitAttributes.  # noqa: E501
        :type sha: str
        :param message: The message of this CommitAttributes.  # noqa: E501
        :type message: str
        :param user_name: The user_name of this CommitAttributes.  # noqa: E501
        :type user_name: str
        :param user_email: The user_email of this CommitAttributes.  # noqa: E501
        :type user_email: str
        """
        self.swagger_types = {
            'sha': str,
            'message': str,
            'user_name': str,
            'user_email': str
        }

        self.attribute_map = {
            'sha': 'sha',
            'message': 'message',
            'user_name': 'user-name',
            'user_email': 'user-email'
        }
        self._sha = sha
        self._message = message
        self._user_name = user_name
        self._user_email = user_email

    @classmethod
    def from_dict(cls, dikt) -> 'CommitAttributes':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Commit_attributes of this CommitAttributes.  # noqa: E501
        :rtype: CommitAttributes
        """
        return util.deserialize_model(dikt, cls)

    @property
    def sha(self) -> str:
        """Gets the sha of this CommitAttributes.


        :return: The sha of this CommitAttributes.
        :rtype: str
        """
        return self._sha

    @sha.setter
    def sha(self, sha: str):
        """Sets the sha of this CommitAttributes.


        :param sha: The sha of this CommitAttributes.
        :type sha: str
        """

        self._sha = sha

    @property
    def message(self) -> str:
        """Gets the message of this CommitAttributes.


        :return: The message of this CommitAttributes.
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message: str):
        """Sets the message of this CommitAttributes.


        :param message: The message of this CommitAttributes.
        :type message: str
        """

        self._message = message

    @property
    def user_name(self) -> str:
        """Gets the user_name of this CommitAttributes.


        :return: The user_name of this CommitAttributes.
        :rtype: str
        """
        return self._user_name

    @user_name.setter
    def user_name(self, user_name: str):
        """Sets the user_name of this CommitAttributes.


        :param user_name: The user_name of this CommitAttributes.
        :type user_name: str
        """

        self._user_name = user_name

    @property
    def user_email(self) -> str:
        """Gets the user_email of this CommitAttributes.


        :return: The user_email of this CommitAttributes.
        :rtype: str
        """
        return self._user_email

    @user_email.setter
    def user_email(self, user_email: str):
        """Sets the user_email of this CommitAttributes.


        :param user_email: The user_email of this CommitAttributes.
        :type user_email: str
        """

        self._user_email = user_email
