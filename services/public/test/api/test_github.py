from fastapi.testclient import TestClient
from public.config import api_prefix
from public.main import app
from public.test.api import SECRET, ApiTestCase
from sonja.test.util import create_repo, run_create_operation, create_ecosystem
from json import dumps
from hmac import HMAC
from hashlib import sha256
from typing import Tuple

client = TestClient(app)


def sign_payload(data: dict) -> Tuple[str, dict]:
    data_str = dumps(data)
    signature = HMAC(key=SECRET.encode(), msg=data_str.encode(), digestmod=sha256).hexdigest()
    return data_str, {"X-Hub-Signature-256": f"sha256={signature}"}


class TestGeneral(ApiTestCase):
    @classmethod
    def setUpClass(cls):
        ApiTestCase.setUpClass()
        ecosystem_id = run_create_operation(create_ecosystem, dict())
        run_create_operation(create_repo, dict(), ecosystem_id)
        run_create_operation(create_repo, {"repo.https": True}, ecosystem_id)

    def setUp(self):
        self.crawler_mock.reset_mock()

    def test_post_ping(self):
        data = {
            "repository": {
                "full_name": "uboot/sonja-backend"
            }}
        payload, headers = sign_payload(data)

        response = client.post(f"{api_prefix}/github/push", data=payload, headers=headers)

        self.assertEqual(202, response.status_code)
        self.crawler_mock.process_repo.assert_not_called()

    def test_post_push_ssh_repo(self):
        data = {
            "after": "10d5538c8b87a74e11c05c119e982b0e999ec77e",
            "ref": "refs/heads/main",
            "repository": {
                "full_name": "uboot/sonja-backend"
            }
        }
        payload, headers = sign_payload(data)

        response = client.post(f"{api_prefix}/github/push", data=payload, headers=headers)

        self.assertEqual(202, response.status_code)
        self.crawler_mock.process_repo.assert_called_with("1", "10d5538c8b87a74e11c05c119e982b0e999ec77e",
                                                          "refs/heads/main")

    def test_post_push_https_repo(self):
        data = {
            "after": "10d5538c8b87a74e11c05c119e982b0e999ec77e",
            "ref": "refs/heads/main",
            "repository": {
                "full_name": "uboot/conan-packages"
            }
        }
        payload, headers = sign_payload(data)

        response = client.post(f"{api_prefix}/github/push", data=payload, headers=headers)

        self.assertEqual(202, response.status_code)
        self.crawler_mock.process_repo.assert_called_with("2", "10d5538c8b87a74e11c05c119e982b0e999ec77e",
                                                          "refs/heads/main")
