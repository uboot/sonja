# coding: utf-8

from __future__ import absolute_import

from conanci import database
from conanci.test import util
from swagger_server.test import BaseTestCase


class TestCommitController(BaseTestCase):
    """CommitController integration test stubs"""

    def setUp(self):
        with database.session_scope() as session:
            commit = util.create_commit()
            session.add(commit)

    def test_get_commit(self):
        """Test case for get_commit

        get a commit
        """
        response = self.client.open(
            '/api/v1/commit/{commit_id}'.format(commit_id=1),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_commits(self):
        """Test case for get_commits

        get the commits of a repo
        """
        response = self.client.open(
            '/api/v1/repo/{repo_id}/commit'.format(repo_id=1),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
