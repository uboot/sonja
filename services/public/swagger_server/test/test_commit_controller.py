# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.commit_data import CommitData  # noqa: E501
from swagger_server.models.commit_list import CommitList  # noqa: E501
from swagger_server.test import BaseTestCase


class TestCommitController(BaseTestCase):
    """CommitController integration test stubs"""

    def test_get_commit(self):
        """Test case for get_commit

        get a commit
        """
        response = self.client.open(
            '/commit/{commitId}'.format(commit_id=789),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_commits(self):
        """Test case for get_commits

        get the commits of a repo
        """
        response = self.client.open(
            '/repo/{repoId}/commit'.format(repo_id=789),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
