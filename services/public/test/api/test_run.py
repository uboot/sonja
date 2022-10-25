from fastapi.testclient import TestClient

from public.config import api_prefix
from public.main import app
from sonja.test.api import ApiTestCase
from sonja.test.util import create_run, run_create_operation

client = TestClient(app)


class TestRun(ApiTestCase):
    @classmethod
    def setUpClass(cls):
        ApiTestCase.setUpClass()

    def test_get_run(self):
        run_id = run_create_operation(create_run, dict())
        response = client.get(f"{api_prefix}/run/{run_id}", headers=self.reader_headers)
        self.assertEqual(200, response.status_code)
        attributes = response.json()["data"]["attributes"]
        self.assertEqual("active", attributes["status"])

    def test_get_run_list(self):
        response = client.get(f"{api_prefix}/build/1/run", headers=self.reader_headers)
        self.assertEqual(200, response.status_code)
        attributes = response.json()["data"][0]["attributes"]
        self.assertEqual("active", attributes["status"])
