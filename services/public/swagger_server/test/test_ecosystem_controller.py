# coding: utf-8

from __future__ import absolute_import

from sonja import database
from sonja.test import util
from flask import json
from swagger_server import models
from swagger_server.test import BaseTestCase


class TestEcosystemController(BaseTestCase):
    """EcosystemController integration test stubs"""

    def setUp(self):
        super().setUp()
        self.login()
        with database.session_scope() as session:
            ecosystem = util.create_ecosystem(dict())
            session.add(ecosystem)

    def test_add_ecosystem(self):
        """Test case for add_ecosystem

        add a new ecosystem
        """
        body = models.EcosystemData(data=models.Ecosystem(
            type="ecosystems",
            attributes=models.EcosystemAttributes(
                name="Company",
                user="company",
                credentials=[
                    models.EcosystemAttributesCredentials(
                        url="https://uboot@github.com",
                        password="Passw0rd",
                        username=""
                    )
                ]
            )
        ))
        response = self.client.open(
            '/api/v1/ecosystem',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert201(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_ecosystem(self):
        """Test case for delete_ecosystem

        delete an ecosystem
        """
        response = self.client.open(
            '/api/v1/ecosystem/{ecosystem_id}'.format(ecosystem_id=1),
            method='DELETE')
        self.assert204(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_ecosystem(self):
        """Test case for get_ecosystem

        get an ecosystem
        """
        response = self.client.open(
            '/api/v1/ecosystem/{ecosystem_id}'.format(ecosystem_id=1),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_ecosystems(self):
        """Test case for get_ecosystems

        get all ecosystems
        """
        response = self.client.open(
            '/api/v1/ecosystem',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_ecosystem(self):
        """Test case for update_ecosystem

        update an ecosystem
        """
        body = models.EcosystemData(data=models.Ecosystem(
            type="ecosystems",
            attributes=models.EcosystemAttributes(
                name="Company",
                user="company",
                credentials=[
                    models.EcosystemAttributesCredentials(
                        url="https://github.com",
                        username="user",
                        password="Passw0rd"
                    )
                ]
            )
        ))
        response = self.client.open(
            '/api/v1/ecosystem/{ecosystem_id}'.format(ecosystem_id=1),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
