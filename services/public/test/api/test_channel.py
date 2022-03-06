from fastapi.testclient import TestClient

from public.config import api_prefix
from public.main import app
from sonja.test.api import ApiTestCase
from sonja.test.util import create_channel, create_ecosystem, run_create_operation

client = TestClient(app)


class TestChannel(ApiTestCase):
    @classmethod
    def setUpClass(cls):
        ApiTestCase.setUpClass()
        run_create_operation(create_channel, dict())

    def test_post_channel(self):
        ecosystem_id = run_create_operation(create_ecosystem, dict())
        response = client.post(f"{api_prefix}/channel", json={
            "data": {
                "type": "channels",
                "attributes": {
                    "name": "Releases",
                    "conan_channel": "stable",
                    "branch": "master"
                },
                "relationships": {
                    "ecosystem": {
                        "data": {
                            "id": f"{ecosystem_id}",
                            "type": "ecosystems"
                        }
                    }
                }
            }
        }, headers=self.user_headers)
        self.assertEqual(201, response.status_code)
        attributes = response.json()["data"]["attributes"]
        self.assertEqual("stable", attributes["conan_channel"])
        self.assertEqual("master", attributes["branch"])
        self.assertEqual(f"{ecosystem_id}", response.json()["data"]["relationships"]["ecosystem"]["data"]["id"])

    def test_patch_channel(self):
        channel_id = run_create_operation(create_channel, dict())
        response = client.patch(f"{api_prefix}/channel/{channel_id}", json={
            "data": {
                "type": "channels",
                "attributes": {
                    "name": "test_patch_channel"
                }
            }
        }, headers=self.user_headers)
        self.assertEqual(200, response.status_code)
        attributes = response.json()["data"]["attributes"]
        self.assertEqual("test_patch_channel", attributes["name"])

    def test_get_channel(self):
        channel_id = run_create_operation(create_channel, dict())
        response = client.get(f"{api_prefix}/channel/{channel_id}", headers=self.reader_headers)
        self.assertEqual(200, response.status_code)

    def test_delete_channel(self):
        channel_id = run_create_operation(create_channel, dict())
        response = client.delete(f"{api_prefix}/channel/{channel_id}", headers=self.user_headers)
        self.assertEqual(200, response.status_code)
