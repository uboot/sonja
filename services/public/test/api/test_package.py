from fastapi.testclient import TestClient

from public.config import api_prefix
from public.main import app
from sonja.test.api import ApiTestCase
from sonja.test.util import create_package, run_create_operation

client = TestClient(app)


class TestPackage(ApiTestCase):
    @classmethod
    def setUpClass(cls):
        ApiTestCase.setUpClass()
        run_create_operation(create_package, dict())

    def test_get_package(self):
        package_id = run_create_operation(create_package, dict())
        response = client.get(f"{api_prefix}/package/{package_id}", headers=self.reader_headers)
        self.assertEqual(200, response.status_code)

    def test_get_package_with_build(self):
        package_id = run_create_operation(create_package, {"build.with_dependencies": True})
        response = client.get(f"{api_prefix}/package/{package_id}", headers=self.reader_headers)
        self.assertEqual(200, response.status_code)
