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
        super().setUp()
        with database.session_scope() as session:
            ecosystem = util.create_ecosystem(dict())
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
            method='POST')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_restore(self):
        """Test case for restore

        log out
        """
        body = models.User(user="user")
        self.login()
        response = self.client.open(
            '/api/v1/restore',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_restore_not_authenticated(self):
        """Test case for restore

        log out
        """
        body = models.User(user="user")
        response = self.client.open(
            '/api/v1/restore',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert401(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_restore_wrong_user(self):
        """Test case for restore

        log out
        """
        body = models.User(user="wrong_user")
        response = self.client.open(
            '/api/v1/restore',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert401(response,
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

    def test_clear_ecosystems_no_tables(self):
        """Test case for clear_ecosystems

        remove all entries but the ecosystems from the database
        """
        self.login()
        database.clear_ecosystems()
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

    def test_process_repo(self):
        """Test case for process_repo

        scan repos for new commits
        """
        response = self.client.open(
            '/process-repo/{repoId}'.format(repo_id='1'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
