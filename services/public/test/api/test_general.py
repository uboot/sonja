from fastapi.testclient import TestClient

from public.config import api_prefix
from public.main import app
from public.test.api import ApiTestCase
from sonja.test.util import create_ecosystem, run_create_operation
from sonja.demo import populate_database

client = TestClient(app)


class TestGeneral(ApiTestCase):
    def SetUp(self):
        self.crawler_mock.reset_mock()

    def test_get_clear_ecosystems(self):
        run_create_operation(create_ecosystem, dict())
        response = client.get(f"{api_prefix}/clear_ecosystems", headers=self.admin_headers)
        self.assertEqual(200, response.status_code)

    def test_populate_database(self):
        run_create_operation(create_ecosystem, dict())
        response = client.get(f"{api_prefix}/populate_database", headers=self.admin_headers)
        self.assertEqual(200, response.status_code)

    def test_add_build(self):
        run_create_operation(create_ecosystem, dict())
        populate_database()
        response = client.get(f"{api_prefix}/add_build", headers=self.admin_headers)
        self.assertEqual(200, response.status_code)

    def test_process_repo(self):
        response = client.get(f"{api_prefix}/process_repo/1", headers=self.user_headers)
        self.assertEqual(200, response.status_code)
        self.crawler_mock.process_repo.assert_called_with("1")
