from fastapi.testclient import TestClient

from public.config import api_prefix
from public.main import app
from sonja.test.api import ApiTestCase
from sonja.test.util import create_profile, create_ecosystem, run_create_operation

client = TestClient(app)


class TestProfile(ApiTestCase):
    @classmethod
    def setUpClass(cls):
        ApiTestCase.setUpClass()
        run_create_operation(create_profile, dict())

    def test_post_profile(self):
        ecosystem_id = run_create_operation(create_ecosystem, dict())
        response = client.post(f"{api_prefix}/profile", json={
            "data": {
                "type": "profiles",
                "attributes": {
                    "name": "test_post_profile",
                    "platform": "windows",
                    "labels": [{
                        "label": "embedded"
                    }]
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
        self.assertEqual("test_post_profile", attributes["name"])
        self.assertEqual("windows", attributes["platform"])
        self.assertEqual("embedded", attributes["labels"][0]["label"])
        self.assertEqual(f"{ecosystem_id}", response.json()["data"]["relationships"]["ecosystem"]["data"]["id"])

    def test_patch_profile(self):
        profile_id = run_create_operation(create_profile, dict())
        response = client.patch(f"{api_prefix}/profile/{profile_id}", json={
            "data": {
                "type": "profiles",
                "attributes": {
                    "name": "test_patch_profile",
                    "platform": "windows",
                    "labels": [{
                        "label": "test_label"
                    }]
                }
            }
        }, headers=self.user_headers)
        self.assertEqual(200, response.status_code)
        attributes = response.json()["data"]["attributes"]
        self.assertEqual("test_patch_profile", attributes["name"])
        self.assertEqual("windows", attributes["platform"])
        self.assertEqual("test_label", attributes["labels"][0]["label"])

    def test_get_profile(self):
        profile_id = run_create_operation(create_profile, dict())
        response = client.get(f"{api_prefix}/profile/{profile_id}", headers=self.reader_headers)
        self.assertEqual(200, response.status_code)

    def test_delete_profile(self):
        profile_id = run_create_operation(create_profile, dict())
        response = client.delete(f"{api_prefix}/profile/{profile_id}", headers=self.user_headers)
        self.assertEqual(204, response.status_code)
