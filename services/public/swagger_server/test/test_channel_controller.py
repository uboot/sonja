# coding: utf-8

from __future__ import absolute_import

from conanci import database
from conanci.test import util
from flask import json

from swagger_server import models
from swagger_server.test import BaseTestCase


class TestChannelController(BaseTestCase):

    def setUp(self):
        with database.session_scope() as session:
            channel = util.create_channel()
            session.add(channel)

    def test_add_channel(self):
        """Test case for add_channel

        add a new channel
        """
        body = self.__create_channel("stable", "master")
        response = self.client.open(
            '/channel',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert201(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_channel(self):
        """Test case for delete_channel

        delete a channel
        """
        response = self.client.open(
            '/channel/{channel_id}'.format(channel_id=1),
            method='DELETE')
        self.assert204(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_channel(self):
        """Test case for get_channel

        get a channel
        """
        response = self.client.open(
            '/channel/{channel_id}'.format(channel_id=1),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_channel(self):
        """Test case for update_channel

        update a channel
        """
        body = self.__create_channel("stable", "master")
        response = self.client.open(
            '/channel/{channel_id}'.format(channel_id=1),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def __create_channel(self, name, branch):
        return models.ChannelData(
            data=models.Channel(
                type="channels",
                attributes=models.ChannelAttributes(
                    name=name,
                    branch=branch
                ),
                relationships=models.ProfileRelationships(
                    ecosystem=models.RepoRelationshipsEcosystem(
                        data=models.RepoRelationshipsEcosystemData(
                            type="ecosystems",
                            id=1
                        )
                    )
                )
            )
        )


if __name__ == '__main__':
    import unittest
    unittest.main()
