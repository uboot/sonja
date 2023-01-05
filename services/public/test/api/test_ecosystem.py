from fastapi.testclient import TestClient

from public.config import api_prefix
from public.main import app
from public.test.api import ApiTestCase
from sonja.test.util import create_channel, create_ecosystem, create_profile, run_create_operation

client = TestClient(app)


class TestEcosystem(ApiTestCase):
    def test_get_ecosystems(self):
        run_create_operation(create_ecosystem, dict())
        response = client.get(f"{api_prefix}/ecosystem", headers=self.reader_headers)
        self.assertEqual(200, response.status_code)

    def test_get_ecosystem(self):
        ecosystem_id = run_create_operation(create_ecosystem, dict())
        run_create_operation(create_profile, dict(), ecosystem_id)
        run_create_operation(create_channel, dict(), ecosystem_id)
        response = client.get(f"{api_prefix}/ecosystem/{ecosystem_id}", headers=self.reader_headers)
        self.assertEqual(200, response.status_code)
        attributes = response.json()["data"]["attributes"]
        self.assertEqual(1, len(attributes["conan_credentials"]))

    def test_post_ecosystem(self):
        response = client.post(f"{api_prefix}/ecosystem", json={
            "data": {
                "type": "ecosystems",
                "attributes": {
                    "name": "test_post_ecosystem"
                }
            }
        }, headers=self.user_headers)
        self.assertEqual(201, response.status_code)
        attributes = response.json()["data"]["attributes"]
        self.assertEqual("test_post_ecosystem", attributes["name"])

    def test_patch_ecosystem(self):
        ecosystem_id = run_create_operation(create_ecosystem, dict())
        response = client.patch(f"{api_prefix}/ecosystem/{ecosystem_id}", json={
            "data": {
                "type": "ecosystems",
                "attributes": {
                    "name": "test_patch_ecosystem",
                }
            }
        }, headers=self.user_headers)
        self.assertEqual(200, response.status_code)
        self.assertEqual("test_patch_ecosystem", response.json()["data"]["attributes"]["name"])

    def test_delete_ecosystem(self):
        ecosystem_id = run_create_operation(create_ecosystem, dict())
        response = client.delete(f"{api_prefix}/ecosystem/{ecosystem_id}", headers=self.admin_headers)
        self.assertEqual(200, response.status_code)

    def test_delete_unknown_ecosystem(self):
        response = client.delete(f"{api_prefix}/ecosystem/100", headers=self.admin_headers)
        self.assertEqual(404, response.status_code)
