from fastapi.testclient import TestClient

from public.config import api_prefix
from public.main import app
from sonja.test.api import ApiTestCase, SECRET
from json import dumps
from hmac import HMAC
from hashlib import sha256

client = TestClient(app)


class TestGeneral(ApiTestCase):
    def test_post_ping(self):
        data = dumps({
            "repository": {
                "full_name": "uboot/sonja-backend"
            }
        })
        signature = HMAC(key=SECRET.encode(), msg=data.encode(), digestmod=sha256).hexdigest()

        response = client.post(f"{api_prefix}/github/push", data=data, headers={
            "X-Hub-Signature-256": f"sha256={signature}"
        })
        self.assertEqual(202, response.status_code)

    def test_post_push(self):
        data = dumps({
            "after": "10d5538c8b87a74e11c05c119e982b0e999ec77e",
            "ref": "refs/heads/main",
            "repository": {
                "full_name": "uboot/sonja-backend"
            }
        })
        signature = HMAC(key=SECRET.encode(), msg=data.encode(), digestmod=sha256).hexdigest()

        response = client.post(f"{api_prefix}/github/push", data=data, headers={
            "X-Hub-Signature-256": f"sha256={signature}"
        })
        self.assertEqual(202, response.status_code)
