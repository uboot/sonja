# coding: utf-8

from __future__ import absolute_import

from conanci import database
from conanci.test import util
from flask import json
from swagger_server import models
from swagger_server.test import BaseTestCase


class TestBuildController(BaseTestCase):
    """BuildController integration test stubs"""

    def setUp(self):
        self.login()
        with database.session_scope() as session:
            build = util.create_build({"build.with_dependencies": True})
            session.add(build)

    def test_get_build(self):
        """Test case for get_build

        get a build
        """
        response = self.client.open(
            '/api/v1/build/{build_id}'.format(build_id=1),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_builds(self):
        """Test case for get_builds

        get builds of an ecosystem
        """
        response = self.client.open(
            '/api/v1/ecosystem/{ecosystem_id}/build'.format(ecosystem_id=789),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_build(self):
        """Test case for update_build

        update a build
        """
        body = models.BuildData(
            data=models.Build(
                type="builds",
                attributes=models.BuildAttributes(status="active")
            )
        )
        response = self.client.open(
            '/api/v1/build/{build_id}'.format(build_id=1),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
