from fastapi.testclient import TestClient

from public.config import api_prefix
from public.main import app
from public.test.api import ApiTestCase
from public.crud.configuration import read_configuration

client = TestClient(app)


class TestConfiguration(ApiTestCase):
    def test_get_current_configuration(self):
        response = client.get(f"{api_prefix}/configuration/current", headers=self.admin_headers)
        self.assertEqual(200, response.status_code)

    def test_patch_configuration(self):
        configuration = client.get(f"{api_prefix}/configuration/current", headers=self.admin_headers).json()
        response = client.patch(f"{api_prefix}/configuration/{configuration['data']['id']}", json={
            "data": {
                "type": "configurations",
                "attributes": {
                    "git_credentials": [{
                        "url": "https://url",
                        "username": "user",
                        "password": "password"
                    }],
                    "docker_credentials": [{
                        "server": "server",
                        "username": "user",
                        "password": "password"
                    }]
                }
            }
        }, headers=self.admin_headers)
        self.assertEqual(200, response.status_code)
        attributes = response.json()["data"]["attributes"]
        self.assertDictEqual({"url": "https://url", "username": "user", "password": "password"},
                             attributes["git_credentials"][0])

    def test_patch_configuration_regenerate_github_secret(self):
        configuration = client.get(f"{api_prefix}/configuration/current", headers=self.admin_headers).json()
        response = client.patch(f"{api_prefix}/configuration/{configuration['data']['id']}", json={
            "data": {
                "type": "configurations",
                "attributes": {
                    "github_secret": ""
                }
            }
        }, headers=self.admin_headers)
        self.assertEqual(200, response.status_code)
        attributes = response.json()["data"]["attributes"]
        self.assertEqual(len(attributes["github_secret"]), 40)

    def test_patch_configuration_regenerate_ssh_key(self):
        configuration = client.get(f"{api_prefix}/configuration/current", headers=self.admin_headers).json()
        response = client.patch(f"{api_prefix}/configuration/{configuration['data']['id']}", json={
            "data": {
                "type": "configurations",
                "attributes": {
                    "public_ssh_key": "",
                }
            }
        }, headers=self.admin_headers)
        self.assertEqual(200, response.status_code)
        self.assertEqual(968, len(response.json()["data"]["attributes"]["public_ssh_key"]))
