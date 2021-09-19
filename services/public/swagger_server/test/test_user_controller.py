# coding: utf-8

from __future__ import absolute_import

from sonja import database
from sonja.test import util
from flask import json
from swagger_server import models
from swagger_server.test import BaseTestCase


class TestUserController(BaseTestCase):
    """UserController integration test stubs"""

    def setUp(self):
        super().setUp()
        self.login()

    def test_add_user(self):
        """Test case for add_user

        add a new user
        """
        body = models.UserData(data=models.User(
            type="users",
            attributes=models.UserAttributes(
                user_name="name",
                password="passw0rd",
                permissions=["read", "write"]
            )
        ))
        response = self.client.open(
            '/api/v1/user',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert201(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_add_duplicate_user(self):
        """Test case for add_user

        add a new user
        """
        body = models.UserData(data=models.User(
            type="users",
            attributes=models.UserAttributes(
                user_name="user"
            )
        ))
        response = self.client.open(
            '/api/v1/user',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert400(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_add_user_no_name(self):
        """Test case for add_user

        add a new user
        """
        body = models.UserData(data=models.User(
            type="users",
            attributes=models.UserAttributes(
                password="passw0rd",
            )
        ))
        response = self.client.open(
            '/api/v1/user',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert400(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_add_user_no_password(self):
        """Test case for add_user

        add a new user
        """
        body = models.UserData(data=models.User(
            type="users",
            attributes=models.UserAttributes(
                user_name="name",
            )
        ))
        response = self.client.open(
            '/api/v1/user',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')
        self.assert400(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_user(self):
        """Test case for delete_user

        delete an user
        """
        with database.session_scope() as session:
            user = util.create_user({"user.user_name": "user2"})
            session.add(user)

        response = self.client.open(
            '/api/v1/user/{user_id}'.format(user_id=1),
            method='DELETE')
        self.assert204(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_last_user(self):
        """Test case for delete_user

        delete an user
        """
        response = self.client.open(
            '/api/v1/user/{user_id}'.format(user_id=1),
            method='DELETE')
        self.assert400(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_user(self):
        """Test case for get_user

        get an user
        """
        response = self.client.open(
            '/api/v1/user/{user_id}'.format(user_id=1),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_users(self):
        """Test case for get_users

        get all users
        """
        response = self.client.open(
            '/api/v1/user',
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_user(self):
        body = models.UserData(data=models.User(
            type="users",
            attributes=models.UserAttributes(
                user_name="new_name",
                email="xyz@test.com",
                password="new_password",
                old_password="password",
                permissions=["read", "write"]
            )
        ))
        response = self.client.open(
            '/api/v1/user/{user_id}'.format(user_id=1),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_duplicate_user(self):
        with database.session_scope() as session:
            user = util.create_user({"user.user_name": "user2"})
            session.add(user)

        body = models.UserData(data=models.User(
            type="users",
            attributes=models.UserAttributes(
                user_name="user"
            )
        ))
        response = self.client.open(
            '/api/v1/user/{user_id}'.format(user_id=2),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert400(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_user_wrong_password(self):
        body = models.UserData(data=models.User(
            type="users",
            attributes=models.UserAttributes(
                password="new_password",
                old_password="wrong",
            )
        ))
        response = self.client.open(
            '/api/v1/user/{user_id}'.format(user_id=1),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert400(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_user_no_password(self):
        body = models.UserData(data=models.User(
            type="users",
            attributes=models.UserAttributes(
                user_name="name",
                password=""
            )
        ))
        response = self.client.open(
            '/api/v1/user/{user_id}'.format(user_id=1),
            method='PATCH',
            data=json.dumps(body),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
