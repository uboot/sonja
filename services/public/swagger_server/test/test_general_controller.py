# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.test import BaseTestCase


class TestGeneralController(BaseTestCase):
    """GeneralController integration test stubs"""

    def test_clear_database(self):
        """Test case for clear_database

        remove all entries from the database
        """
        response = self.client.open(
            '/clear-database',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_clear_ecosystems(self):
        """Test case for clear_ecosystems

        remove all entries but the ecosystems from the database
        """
        response = self.client.open(
            '/clear-ecosystems',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_ping(self):
        """Test case for ping

        ping the service
        """
        response = self.client.open(
            '/ping',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_populate_database(self):
        """Test case for populate_database

        populate the database with sample data
        """
        response = self.client.open(
            '/populate-database',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_process_repos(self):
        """Test case for process_repos

        scan repos for new commits
        """
        response = self.client.open(
            '/process-repos',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
