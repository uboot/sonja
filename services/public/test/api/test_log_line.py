from fastapi.testclient import TestClient

from public.config import api_prefix
from public.main import app
from sonja.test.api import ApiTestCase
from sonja.test.util import create_log_line, run_create_operation

client = TestClient(app)


class TestLog(ApiTestCase):
    @classmethod
    def setUpClass(cls):
        ApiTestCase.setUpClass()
        run_create_operation(create_log_line, dict())

    def test_get_log_line_list(self):
        response = client.get(f"{api_prefix}/log_line?run_id=1&page=1&per_page=5", headers=self.reader_headers)
        self.assertEqual(200, response.status_code)
        self.assertGreaterEqual(1, len(response.json()["data"]))

    def test_get_log_line_item(self):
        log_line_id = run_create_operation(create_log_line, dict())
        response = client.get(f"{api_prefix}/log_line/{log_line_id}", headers=self.reader_headers)
        self.assertEqual(200, response.status_code)
