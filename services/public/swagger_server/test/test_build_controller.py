# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.build_data import BuildData  # noqa: E501
from swagger_server.models.build_list import BuildList  # noqa: E501
from swagger_server.test import BaseTestCase


class TestBuildController(BaseTestCase):
    """BuildController integration test stubs"""

    def test_get_build(self):
        """Test case for get_build

        get a build
        """
        response = self.client.open(
            '/build/{build_id}'.format(build_id=1),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_builds(self):
        """Test case for get_builds

        get builds of an ecosystem
        """
        response = self.client.open(
            '/ecosystem/{ecosystem_id}/build'.format(ecosystem_id=789),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_build(self):
        """Test case for update_build

        update a build
        """
        body = BuildData()
        response = self.client.open(
            '/build/{build_id}'.format(build_id=789),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
