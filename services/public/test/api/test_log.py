from fastapi.testclient import TestClient

from public.config import api_prefix
from public.main import app
from sonja.test.api import ApiTestCase
from sonja.test.util import create_log, run_create_operation

client = TestClient(app)


class TestLog(ApiTestCase):
    @classmethod
    def setUpClass(cls):
        ApiTestCase.setUpClass()
        run_create_operation(create_log, dict())

    def test_get_log(self):
        log_id = run_create_operation(create_log, dict())
        response = client.get(f"{api_prefix}/log/{log_id}", headers=self.reader_headers)
        self.assertEqual(200, response.status_code)
