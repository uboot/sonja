from sonja.redis import RedisClient
from sonja.model import Build, Ecosystem, Profile
import unittest

# Requires:
#
# Redis database
# docker run --rm -d --name redis -p 6379:6379 redis:6.2.6


class TestRedis(unittest.TestCase):
    def setUp(self):
        self.redis_client = RedisClient()

    def test_publish_build_update(self):
        ecosystem = Ecosystem()
        profile = Profile()
        profile.ecosystem = ecosystem
        build = Build()
        build.profile = profile
        self.redis_client.publish_build_update(build)

    def test_publish_build_updates(self):
        ecosystem = Ecosystem()
        profile = Profile()
        profile.ecosystem = ecosystem
        build = Build()
        build.profile = profile
        self.redis_client.publish_build_updates([build])
