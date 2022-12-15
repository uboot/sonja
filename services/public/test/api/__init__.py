import unittest

from starlette.datastructures import FormData
from starlette.testclient import TestClient

from public.config import api_prefix
from public.main import app
from public.client import get_crawler, get_linux_agent, get_windows_agent, get_redis_client
from unittest.mock import Mock

from sonja.database import session_scope, reset_database
from sonja.model import Configuration
from sonja.test import util

crawler_mock = Mock()
linux_agent_mock = Mock()
windows_agent_mock = Mock()
redis_client_mock = Mock()


def get_crawler_override():
    return crawler_mock


def get_linux_agent_override():
    return linux_agent_mock


def get_windows_agent_override():
    return windows_agent_mock


def get_redis_client_override():
    return redis_client_mock


app.dependency_overrides[get_crawler] = get_crawler_override
app.dependency_overrides[get_linux_agent] = get_linux_agent_override
app.dependency_overrides[get_windows_agent] = get_windows_agent_override
app.dependency_overrides[get_redis_client] = get_redis_client_override

SECRET = "0123467890abcdef0123467890abcdef"
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
        reset_database()
        with session_scope() as session:
            configuration = Configuration()
            configuration.github_secret = SECRET
            session.add(configuration)

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
        cls.crawler_mock = crawler_mock
        cls.linux_agent_mock = linux_agent_mock
        cls.windows_agent_mock = windows_agent_mock
        cls.redis_client_mock = redis_client_mock