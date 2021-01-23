# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.channel_data import ChannelData  # noqa: E501
from swagger_server.test import BaseTestCase


class TestChannelController(BaseTestCase):
    """ChannelController integration test stubs"""

    def test_add_channel(self):
        """Test case for add_channel

        add a new channel
        """
        body = ChannelData()
        response = self.client.open(
            '/channel',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_channel(self):
        """Test case for delete_channel

        delete a channel
        """
        response = self.client.open(
            '/channel/{channelId}'.format(channel_id=789),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_channel(self):
        """Test case for get_channel

        get a channel
        """
        response = self.client.open(
            '/channel/{channelId}'.format(channel_id=789),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_channel(self):
        """Test case for update_channel

        update a channel
        """
        body = ChannelData()
        response = self.client.open(
            '/channel/{channelId}'.format(channel_id=789),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
