from fastapi.testclient import TestClient

from public.config import api_prefix
from public.main import app
from sonja.test.api import ApiTestCase
from sonja.test.util import create_repo, create_ecosystem, run_create_operation

client = TestClient(app)


class TestRepo(ApiTestCase):
    @classmethod
    def setUpClass(cls):
        ApiTestCase.setUpClass()
        run_create_operation(create_repo, dict())

    def test_post_repo(self):
        ecosystem_id = run_create_operation(create_ecosystem, dict())
        response = client.post(f"{api_prefix}/repo", json={
            "data": {
                "type": "repos",
                "attributes": {
                    "name": "test_post_repo",
                    "url": "https://github.com/uboot/sonja-backend.git",
                    "path": "packages/hello",
                    "version": "1.2.3",
                    "exclude": [{
                        "label": "embedded"
                    }],
                    "options": [{
                        "key": "hello:shared",
                        "value": "True"
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
        self.assertEqual("test_post_repo", attributes["name"])
        self.assertEqual("1.2.3", attributes["version"])
        self.assertDictEqual({"key": "hello:shared", "value": "True"}, attributes["options"][0])
        self.assertDictEqual({"label": "embedded"}, attributes["exclude"][0])
        self.assertEqual(f"{ecosystem_id}", response.json()["data"]["relationships"]["ecosystem"]["data"]["id"])

    def test_patch_repo(self):
        repo_id = run_create_operation(create_repo, dict())
        response = client.patch(f"{api_prefix}/repo/{repo_id}", json={
            "data": {
                "type": "repos",
                "attributes": {
                    "name": "test_patch_repo"
                }
            }
        }, headers=self.user_headers)
        self.assertEqual(200, response.status_code)
        attributes = response.json()["data"]["attributes"]
        self.assertEqual("test_patch_repo", attributes["name"])

    def test_get_repo(self):
        repo_id = run_create_operation(create_repo, dict())
        response = client.get(f"{api_prefix}/repo/{repo_id}", headers=self.reader_headers)
        self.assertEqual(200, response.status_code)

    def test_get_repos(self):
        response = client.get(f"{api_prefix}/ecosystem/1/repo", headers=self.reader_headers)
        self.assertEqual(200, response.status_code)

    def test_delete_repo(self):
        repo_id = run_create_operation(create_repo, dict())
        response = client.delete(f"{api_prefix}/repo/{repo_id}", headers=self.user_headers)
        self.assertEqual(200, response.status_code)
