from fastapi.testclient import TestClient

from public.config import api_prefix
from public.main import app
from sonja.model import BuildStatus
from public.test.api import ApiTestCase
from sonja.test.util import create_build, create_ecosystem, run_create_operation

client = TestClient(app)


class TestBuild(ApiTestCase):
    @classmethod
    def setUpClass(cls):
        ApiTestCase.setUpClass()
        ecosystem = create_ecosystem(dict());
        run_create_operation(create_build, {"ecosystem": ecosystem})
        run_create_operation(create_build, {"ecosystem": ecosystem})

    def test_patch_stop_active_build(self):
        build_id = run_create_operation(create_build, {"build.status": BuildStatus.active})
        response = client.patch(f"{api_prefix}/build/{build_id}", json={
            "data": {
                "type": "builds",
                "attributes": {
                    "status": "stopping"
                }
            }
        }, headers=self.user_headers)
        self.assertEqual(200, response.status_code)
        attributes = response.json()["data"]["attributes"]
        self.assertEqual("stopping", attributes["status"])

    def test_patch_stop_new_build(self):
        build_id = run_create_operation(create_build, {"build.status": BuildStatus.new})
        response = client.patch(f"{api_prefix}/build/{build_id}", json={
            "data": {
                "type": "builds",
                "attributes": {
                    "status": "stopping"
                }
            }
        }, headers=self.user_headers)
        self.assertEqual(200, response.status_code)
        attributes = response.json()["data"]["attributes"]
        self.assertEqual("stopped", attributes["status"])

    def test_patch_start_active_build(self):
        build_id = run_create_operation(create_build, {"build.status": BuildStatus.active})
        response = client.patch(f"{api_prefix}/build/{build_id}", json={
            "data": {
                "type": "builds",
                "attributes": {
                    "status": "new"
                }
            }
        }, headers=self.user_headers)
        self.assertEqual(200, response.status_code)
        attributes = response.json()["data"]["attributes"]
        self.assertEqual("active", attributes["status"])

    def test_patch_start_stopping_build(self):
        build_id = run_create_operation(create_build, {"build.status": BuildStatus.stopping})
        response = client.patch(f"{api_prefix}/build/{build_id}", json={
            "data": {
                "type": "builds",
                "attributes": {
                    "status": "new"
                }
            }
        }, headers=self.user_headers)
        self.assertEqual(200, response.status_code)
        attributes = response.json()["data"]["attributes"]
        self.assertEqual("stopping", attributes["status"])

    def test_get_build(self):
        build_id = run_create_operation(create_build, dict())
        response = client.get(f"{api_prefix}/build/{build_id}", headers=self.reader_headers)
        self.assertEqual(200, response.status_code)
        attributes = response.json()["data"]["attributes"]
        self.assertEqual("new", attributes["status"])

    def test_get_build_list(self):
        response = client.get(f"{api_prefix}/build?ecosystem_id=1", headers=self.reader_headers)
        self.assertEqual(200, response.status_code)
        self.assertGreater(len(response.json()["data"]), 1)
        attributes = response.json()["data"][0]["attributes"]
        self.assertEqual("new", attributes["status"])

    def test_get_build_list_paged(self):
        response = client.get(f"{api_prefix}/build?ecosystem_id=1&page=2&per_page=1", headers=self.reader_headers)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.json()["data"]))
        attributes = response.json()["data"][0]["attributes"]
        self.assertEqual("new", attributes["status"])

    def test_get_build_list_with_profile_and_channel(self):
        response = client.get(f"{api_prefix}/build?ecosystem_id=1&channel_id=1&profile_id=1&page=1&per_page=5",
                              headers=self.reader_headers)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.json()["data"]))
        attributes = response.json()["data"][0]["attributes"]
        self.assertEqual("new", attributes["status"])

    def test_get_build_list_with_repo(self):
        response = client.get(f"{api_prefix}/build?ecosystem_id=1&repo_id=1",
                              headers=self.reader_headers)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.json()["data"]))
        attributes = response.json()["data"][0]["attributes"]
        self.assertEqual("new", attributes["status"])

    def test_get_build_list_with_profile(self):
        response = client.get(f"{api_prefix}/build?ecosystem_id=1&profile_id=1",
                              headers=self.reader_headers)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.json()["data"]))
        attributes = response.json()["data"][0]["attributes"]
        self.assertEqual("new", attributes["status"])

    def test_get_build_list_with_channel(self):
        response = client.get(f"{api_prefix}/build?ecosystem_id=1&channel_id=1",
                              headers=self.reader_headers)
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.json()["data"]))
        attributes = response.json()["data"][0]["attributes"]
        self.assertEqual("new", attributes["status"])

    def test_get_build_list_with_unknown_profile_and_channel(self):
        response = client.get(f"{api_prefix}/build?ecosystem_id=1&channel_id=-1&profile_id=-1&page=1&per_page=5",
                              headers=self.reader_headers)
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.json()["data"]))
