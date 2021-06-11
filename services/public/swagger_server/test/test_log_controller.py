# coding: utf-8

from __future__ import absolute_import

from conanci import database
from conanci.test import util
from swagger_server.test import BaseTestCase


class TestLogController(BaseTestCase):
    """LogController integration test stubs"""

    def setUp(self):
        super().setUp()
        self.login()
        with database.session_scope() as session:
            log = util.create_log(dict())
            session.add(log)

    def test_get_log(self):
        """Test case for get_log

        get a log
        """
        response = self.client.open(
            '/api/v1/log/{log_id}'.format(log_id=1),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
