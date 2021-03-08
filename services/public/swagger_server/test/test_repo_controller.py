# coding: utf-8

from __future__ import absolute_import

from conanci import database
from conanci.test import util
from flask import json
from swagger_server import models
from swagger_server.test import BaseTestCase


class TestRepoController(BaseTestCase):
    """RepoController integration test stubs"""

    def setUp(self):
        self.login()
        with database.session_scope() as session:
            repo = util.create_repo()
            session.add(repo)

    def test_add_repo(self):
        """Test case for add_repo

        add a new repo
        """
        body = self.__create_repo("hello", "git@github.com:uboot/conan-ci.git", "packages/hello")
        response = self.client.open(
            '/api/v1/repo',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert201(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_repo(self):
        """Test case for delete_repo

        delete a repo
        """
        response = self.client.open(
            '/api/v1/repo/{repo_id}'.format(repo_id=1),
            method='DELETE')
        self.assert204(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_repo(self):
        """Test case for get_repo

        get a repo
        """
        response = self.client.open(
            '/api/v1/repo/{repo_id}'.format(repo_id=1),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_repos(self):
        """Test case for get_repos

        get repos of an ecosystem
        """
        response = self.client.open(
            '/api/v1/ecosystem/{ecosystem_id}/repo'.format(ecosystem_id=1),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_repo(self):
        """Test case for update_repo

        update a repo
        """
        body = self.__create_repo("hello", "git@github.com:uboot/conan-ci.git", "packages/hello")
        response = self.client.open(
            '/api/v1/repo/{repo_id}'.format(repo_id=1),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def __create_repo(self, name, url, path):
        return models.RepoData(
            data=models.Repo(
                type="repos",
                attributes=models.RepoAttributes(
                    name=name,
                    url=url,
                    path=path
                ),
                relationships=models.RepoRelationships(
                    ecosystem=models.RepoRelationshipsEcosystem(
                        data=models.RepoRelationshipsEcosystemData(
                            type="ecosystems",
                            id="1"
                        )
                    )
                )
            )
        )


if __name__ == '__main__':
    import unittest
    unittest.main()
