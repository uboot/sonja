# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.ecosystem_data import EcosystemData  # noqa: E501
from swagger_server.models.ecosystem_list import EcosystemList  # noqa: E501
from swagger_server.test import BaseTestCase


class TestEcosystemController(BaseTestCase):
    """EcosystemController integration test stubs"""

    def test_add_ecosystem(self):
        """Test case for add_ecosystem

        add a new ecosystem
        """
        body = EcosystemData()
        response = self.client.open(
            '/ecosystem',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_ecosystem(self):
        """Test case for delete_ecosystem

        delete an ecosystem
        """
        response = self.client.open(
            '/ecosystem/{ecosystemId}'.format(ecosystem_id=789),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_ecosystem(self):
        """Test case for get_ecosystem

        get an ecosystem
        """
        response = self.client.open(
            '/ecosystem/{ecosystemId}'.format(ecosystem_id=789),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_ecosystems(self):
        """Test case for get_ecosystems

        get all ecosystems
        """
        response = self.client.open(
            '/ecosystem',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_ecosystem(self):
        """Test case for update_ecosystem

        update an ecosystem
        """
        body = EcosystemData()
        response = self.client.open(
            '/ecosystem/{ecosystemId}'.format(ecosystem_id=789),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
