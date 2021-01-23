# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.repo_data import RepoData  # noqa: E501
from swagger_server.models.repo_list import RepoList  # noqa: E501
from swagger_server.test import BaseTestCase


class TestRepoController(BaseTestCase):
    """RepoController integration test stubs"""

    def test_add_repo(self):
        """Test case for add_repo

        add a new repo
        """
        body = RepoData()
        response = self.client.open(
            '/repo',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_repo(self):
        """Test case for delete_repo

        delete a repo
        """
        response = self.client.open(
            '/repo/{repoId}'.format(repo_id=789),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_repo(self):
        """Test case for get_repo

        get a repo
        """
        response = self.client.open(
            '/repo/{repoId}'.format(repo_id=789),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_repos(self):
        """Test case for get_repos

        get repos of an ecosystem
        """
        response = self.client.open(
            '/ecosystem/{ecosystemId}/repo'.format(ecosystem_id=789),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_repo(self):
        """Test case for update_repo

        update a repo
        """
        body = RepoData()
        response = self.client.open(
            '/repo/{repoId}'.format(repo_id=789),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
