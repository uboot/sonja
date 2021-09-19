# coding: utf-8

from __future__ import absolute_import

from sonja import database
from sonja.test import util
from swagger_server.test import BaseTestCase


class TestPackageController(BaseTestCase):
    """PackageController integration test stubs"""

    def setUp(self):
        super().setUp()
        self.login()
        with database.session_scope() as session:
            ecosystem = util.create_package(dict())
            session.add(ecosystem)

    def test_get_package(self):
        """Test case for get_package

        get a package
        """
        response = self.client.open(
            '/api/v1/package/{package_id}'.format(package_id=1),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
