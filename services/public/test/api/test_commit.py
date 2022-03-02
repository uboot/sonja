from fastapi.testclient import TestClient

from public.config import api_prefix
from public.main import app
from sonja.test.api import ApiTestCase
from sonja.test.util import create_commit, run_create_operation

client = TestClient(app)


class TestCommit(ApiTestCase):
    @classmethod
    def setUpClass(cls):
        ApiTestCase.setUpClass()
        run_create_operation(create_commit, dict())

    def test_get_commit(self):
        commit_id = run_create_operation(create_commit, dict())
        response = client.get(f"{api_prefix}/commit/{commit_id}", headers=self.reader_headers)
        self.assertEqual(200, response.status_code)

    def test_get_commits(self):
        response = client.get(f"{api_prefix}/repo/1/commit", headers=self.reader_headers)
        self.assertEqual(200, response.status_code)
