from fastapi.testclient import TestClient

from public.config import api_prefix
from public.main import app
from sonja.test.api import ApiTestCase
from sonja.test.util import create_user, run_create_operation

client = TestClient(app)


class TestUser(ApiTestCase):
    def test_get_current_user(self):
        response = client.get(f"{api_prefix}/user/me", headers=self.reader_headers)
        self.assertEqual(200, response.status_code)

    def test_get_user(self):
        response = client.get(f"{api_prefix}/user/1", headers=self.reader_headers)
        self.assertEqual(200, response.status_code)

    def test_get_users(self):
        response = client.get(f"{api_prefix}/user", headers=self.reader_headers)
        self.assertEqual(200, response.status_code)

    def test_create_user(self):
        response = client.post(f"{api_prefix}/user", json={
            "data": {
                "type": "users",
                "attributes": {
                    "user_name": "test_create_user",
                    "permissions": []
                }
            }
        }, headers=self.admin_headers)
        self.assertEqual(201, response.status_code)

    def test_patch_user(self):
        user_id = run_create_operation(create_user, {"user.user_name": "test_update_user"})
        response = client.patch(f"{api_prefix}/user/{user_id}", json={
            "data": {
                "type": "users",
                "attributes": {
                    "first_name": "First",
                    "password": "new_password",
                    "permissions": ["read"]
                }
            }
        }, headers=self.admin_headers)
        self.assertEqual(200, response.status_code)
        self.assertEqual("First", response.json()["data"]["attributes"]["first_name"])

    def test_patch_my_user(self):
        response = client.patch(f"{api_prefix}/user/3", json={
            "data": {
                "type": "users",
                "attributes": dict()
            }
        }, headers=self.reader_headers)
        self.assertEqual(200, response.status_code)

    def test_patch_my_password(self):
        response = client.patch(f"{api_prefix}/user/3", json={
            "data": {
                "type": "users",
                "attributes": {
                    "password": "password",
                    "old_password": "password"
                }
            }
        }, headers=self.reader_headers)
        self.assertEqual(200, response.status_code)

    def test_patch_my_password_fails(self):
        response = client.patch(f"{api_prefix}/user/3", json={
            "data": {
                "type": "users",
                "attributes": {
                    "password": "new_password"
                }
            }
        }, headers=self.reader_headers)
        self.assertEqual(403, response.status_code)

    def test_patch_different_user(self):
        response = client.patch(f"{api_prefix}/user/2", json={
            "data": {
                "type": "users",
                "attributes": dict()
            }
        }, headers=self.reader_headers)
        self.assertEqual(403, response.status_code)

    def test_delete_user(self):
        user_id = run_create_operation(create_user, {"user.user_name": "test_delete_user"})
        response = client.delete(f"{api_prefix}/user/{user_id}", headers=self.admin_headers)
        self.assertEqual(204, response.status_code)

        response = client.get(f"{api_prefix}/user/{user_id}", headers=self.admin_headers)
        self.assertEqual(404, response.status_code)

    def test_delete_current_user(self):
        response = client.delete(f"{api_prefix}/user/1", headers=self.admin_headers)
        self.assertEqual(400, response.status_code)
