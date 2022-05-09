from fastapi.testclient import TestClient
from json import loads
from asyncio import run
from aioredis import create_redis

from public.config import api_prefix
from public.main import app
from sonja.model import BuildStatus
from sonja.test.api import ApiTestCase
from sonja.test.util import create_build, run_create_operation

client = TestClient(app)


class TestBuild(ApiTestCase):
    @classmethod
    def setUpClass(cls):
        ApiTestCase.setUpClass()
        run_create_operation(create_build, dict())

    def test_patch_stop_active_build(self):
        build_id = run_create_operation(create_build, {"build.status": BuildStatus.active})
        response = client.patch(f"{api_prefix}/build/{build_id}", json={
            "data": {
                "type": "builds",
                "attributes": {
                    "status": "stopping"
                }
            }
        }, headers=self.user_headers)
        self.assertEqual(200, response.status_code)
        attributes = response.json()["data"]["attributes"]
        self.assertEqual("stopping", attributes["status"])

    def test_patch_stop_new_build(self):
        build_id = run_create_operation(create_build, {"build.status": BuildStatus.new})
        response = client.patch(f"{api_prefix}/build/{build_id}", json={
            "data": {
                "type": "builds",
                "attributes": {
                    "status": "stopping"
                }
            }
        }, headers=self.user_headers)
        self.assertEqual(200, response.status_code)
        attributes = response.json()["data"]["attributes"]
        self.assertEqual("stopped", attributes["status"])

    def test_patch_start_active_build(self):
        build_id = run_create_operation(create_build, {"build.status": BuildStatus.active})
        response = client.patch(f"{api_prefix}/build/{build_id}", json={
            "data": {
                "type": "builds",
                "attributes": {
                    "status": "new"
                }
            }
        }, headers=self.user_headers)
        self.assertEqual(200, response.status_code)
        attributes = response.json()["data"]["attributes"]
        self.assertEqual("active", attributes["status"])

    def test_patch_start_stopping_build(self):
        build_id = run_create_operation(create_build, {"build.status": BuildStatus.stopping})
        response = client.patch(f"{api_prefix}/build/{build_id}", json={
            "data": {
                "type": "builds",
                "attributes": {
                    "status": "new"
                }
            }
        }, headers=self.user_headers)
        self.assertEqual(200, response.status_code)
        attributes = response.json()["data"]["attributes"]
        self.assertEqual("stopping", attributes["status"])

    def test_get_build(self):
        build_id = run_create_operation(create_build, dict())
        response = client.get(f"{api_prefix}/build/{build_id}", headers=self.reader_headers)
        self.assertEqual(200, response.status_code)
        attributes = response.json()["data"]["attributes"]
        self.assertEqual("new", attributes["status"])

    def test_get_build_list(self):
        response = client.get(f"{api_prefix}/build?ecosystem_id=1&page=1&per_page=5", headers=self.reader_headers)
        self.assertEqual(200, response.status_code)
        attributes = response.json()["data"][0]["attributes"]
        self.assertEqual("new", attributes["status"])

    def test_get_sse_builds(self):
        pass
        # async def send_data():
        #     redis = await create_redis("redis://127.0.0.1")
        #     await redis.publish_json("default", {"test": "Hello"})
        # run(send_data())

        # response = client.get(f"{api_prefix}/sse/ecosystem/1/build", headers=self.reader_headers, stream=True)
        #
        #
        # for line in response.iter_lines():
        #     if line:
        #         decoded_line = line.decode('utf-8')
        #         print(loads(decoded_line))
        # self.assertEqual(200, response.status_code)
