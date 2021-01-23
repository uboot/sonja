# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.profile_data import ProfileData  # noqa: E501
from swagger_server.test import BaseTestCase


class TestProfileController(BaseTestCase):
    """ProfileController integration test stubs"""

    def test_add_profile(self):
        """Test case for add_profile

        add a new profile
        """
        body = ProfileData()
        response = self.client.open(
            '/profile',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_profile(self):
        """Test case for delete_profile

        delete a profile
        """
        response = self.client.open(
            '/profile/{profileId}'.format(profile_id=789),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_profile(self):
        """Test case for get_profile

        get a profile
        """
        response = self.client.open(
            '/profile/{profileId}'.format(profile_id=789),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_profile(self):
        """Test case for update_profile

        update a profile
        """
        body = ProfileData()
        response = self.client.open(
            '/profile/{profileId}'.format(profile_id=789),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
