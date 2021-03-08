# coding: utf-8

from __future__ import absolute_import

from conanci import database
from conanci.test import util
from flask import json
from swagger_server import models
from swagger_server.test import BaseTestCase


class TestGeneralController(BaseTestCase):
    """GeneralController integration test stubs"""

    def setUp(self):
        with database.session_scope() as session:
            ecosystem = util.create_ecosystem()
            session.add(ecosystem)

    def test_login(self):
        """Test case for login

        log in
        """
        body = models.Credentials(user="user", password="paSSwOrd")
        response = self.client.open(
            '/api/v1/login',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_logout(self):
        """Test case for logout

        log out
        """
        self.login()
        response = self.client.open(
            '/api/v1/logout',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_clear_database(self):
        """Test case for clear_database

        remove all entries from the database
        """
        self.login()
        response = self.client.open(
            '/api/v1/clear-database',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_clear_ecosystems(self):
        """Test case for clear_ecosystems

        remove all entries but the ecosystems from the database
        """
        self.login()
        response = self.client.open(
            '/api/v1/clear-ecosystems',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_ping(self):
        """Test case for ping

        ping the service
        """
        response = self.client.open(
            '/api/v1/ping',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_populate_database(self):
        """Test case for populate_database

        populate the database with sample data
        """
        self.login()
        response = self.client.open(
            '/api/v1/populate-database',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_process_repos(self):
        """Test case for process_repos

        scan repos for new commits
        """
        self.login()
        response = self.client.open(
            '/api/v1/process-repos',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
