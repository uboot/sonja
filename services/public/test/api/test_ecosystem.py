from fastapi.testclient import TestClient

from public.config import api_prefix
from public.main import app
from sonja.test.api import ApiTestCase
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

    def test_post_ecosystem(self):
        response = client.post(f"{api_prefix}/ecosystem", json={
            "data": {
                "type": "ecosystems",
                "attributes": {
                    "name": "test_post_ecosystem",
                    "credentials": [{
                        "url": "https://url",
                        "username": "user",
                        "password": "password"
                    }]
                }
            }
        }, headers=self.user_headers)
        self.assertEqual(201, response.status_code)
        self.assertEqual("test_post_ecosystem", response.json()["data"]["attributes"]["name"])
        attributes = response.json()["data"]["attributes"]
        self.assertDictEqual({"url": "https://url", "username": "user", "password": "password"},
                             attributes["credentials"][0])

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
        self.assertEqual(204, response.status_code)

    def test_delete_unknown_ecosystem(self):
        response = client.delete(f"{api_prefix}/ecosystem/100", headers=self.admin_headers)
        self.assertEqual(404, response.status_code)
