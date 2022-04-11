from sonja.model import Build
from sonja.config import logger
from typing import List
from os import environ
from redis import Redis, ConnectionError
from contextlib import contextmanager
from json import dumps


redis_host = environ.get("REDIS_HOST", "127.0.0.1")


@contextmanager
def get_redis():
    redis = Redis(host=redis_host)
    try:
        yield redis
    finally:
        redis.close()


class RedisClient(object):
    def publish_build_updates(self, builds: List[Build]):
        try:
            with get_redis() as redis:
                for build in builds:
                    logger.debug("Publish update for build '%s' on channel '%s'", build.id, f"ecosystem:{build.id}:build")
                    redis.publish(f"ecosystem:{build.ecosystem.id}:build", dumps({"id": build.id}))
        except ConnectionError as e:
            logger.error("Failed to publish builds: %s", e)

    def publish_build_update(self, build: Build):
        self.publish_build_updates([build])