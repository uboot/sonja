from sonja.redis import RedisClient
from sonja.model import Build
import unittest

# Requires:
#
# Redis database
# docker run --rm -d --name redis -p 6379:6379 redis:6.2.6


class TestRedis(unittest.TestCase):
    def setUp(self):
        self.redis_client = RedisClient()

    def test_publish_build_update(self):
        build = Build()
        self.redis_client.publish_build_update(build)

    def test_publish_build_updates(self):
        build = Build()
        self.redis_client.publish_build_updates([build])


