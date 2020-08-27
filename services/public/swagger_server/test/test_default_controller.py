# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.profile import Profile  # noqa: E501
from swagger_server.models.repo import Repo  # noqa: E501
from swagger_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_add_profile(self):
        """Test case for add_profile

        add a new profile
        """
        body = Profile()
        response = self.client.open(
            '/profile',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_add_repo(self):
        """Test case for add_repo

        add a new repo
        """
        body = Repo()
        response = self.client.open(
            '/repo',
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
            '/profile/{profileId}'.format(profile_id=56),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_repo(self):
        """Test case for delete_repo

        delete a repo
        """
        response = self.client.open(
            '/repo/{repoId}'.format(repo_id=56),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_profiles(self):
        """Test case for get_profiles

        get all active profiles
        """
        response = self.client.open(
            '/profile',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_repos(self):
        """Test case for get_repos

        get all current repos
        """
        response = self.client.open(
            '/repo',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_profile(self):
        """Test case for update_profile

        update an existing profile
        """
        body = Profile()
        response = self.client.open(
            '/profile',
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_repo(self):
        """Test case for update_repo

        update an existing repo
        """
        body = Repo()
        response = self.client.open(
            '/repo',
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
