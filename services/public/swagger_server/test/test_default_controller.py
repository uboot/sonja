# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.build import Build  # noqa: E501
from swagger_server.models.channel import Channel  # noqa: E501
from swagger_server.models.profile import Profile  # noqa: E501
from swagger_server.models.repo import Repo  # noqa: E501
from swagger_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_add_channel(self):
        """Test case for add_channel

        add a new channel
        """
        body = Channel()
        response = self.client.open(
            '/channel',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

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

    def test_delete_channel(self):
        """Test case for delete_channel

        delete a channel
        """
        response = self.client.open(
            '/channel/{channelId}'.format(channel_id=56),
            method='DELETE')
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

    def test_get_builds(self):
        """Test case for get_builds

        get builds
        """
        response = self.client.open(
            '/build/{buildStatus}'.format(build_status='build_status_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_channels(self):
        """Test case for get_channels

        get all channels
        """
        response = self.client.open(
            '/channel',
            method='GET')
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

        Populate the database with sample data
        """
        response = self.client.open(
            '/populate-database',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_build(self):
        """Test case for update_build

        update a build
        """
        body = Build()
        response = self.client.open(
            '/put/{buildId}'.format(build_id=56),
            method='PUT',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
