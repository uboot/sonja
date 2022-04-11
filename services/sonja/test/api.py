from fastapi.testclient import TestClient
from fastapi_plugins import redis_plugin
from starlette.datastructures import FormData

from public.main import app
from public.config import api_prefix
from sonja.database import reset_database, get_session, session_scope
from sonja.test import util

import asyncio
import unittest


client = TestClient(app)


def _header_for_user(user_params: dict()):
    with session_scope() as session:
        user = util.create_user(user_params)
        user_name = user.user_name
        session.add(user)

    response = client.post(f"{api_prefix}/token",
                           FormData([("grant_type", "password"),
                                     ("username", user_name),
                                     ("password", "password")]))

    tokens = response.json()
    a_token = tokens["access_token"]
    return {"Authorization": f"Bearer {a_token}"}


class ApiTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not redis_plugin.redis:
            asyncio.run(redis_plugin.init_app(app))
            asyncio.run(redis_plugin.init())

        reset_database()

        cls.admin_headers = _header_for_user({
            "user.user_name": "admin"
        })
        cls.user_headers = _header_for_user({
            "user.permissions": "write"
        })
        cls.reader_headers = _header_for_user({
            "user.user_name": "reader",
            "user.permissions": "read"
        })
