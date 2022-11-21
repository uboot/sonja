from sonja.model import Build, LogLine, Run
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
                    channel = f"repo:{build.commit.repo.id}:build"
                    logger.debug("Publish update for build '%s' on channel '%s'", build.id, channel)
                    redis.publish(channel, dumps({"id": build.id}))
        except ConnectionError as e:
            logger.error("Failed to publish builds: %s", e)

    def publish_build_update(self, build: Build):
        self.publish_build_updates([build])

    def publish_log_line_update(self, log_line: LogLine):
        try:
            with get_redis() as redis:
                channel = f"run:{log_line.run.id}:log_line"
                logger.debug("Publish update for log line '%s' on channel '%s'", log_line.id, channel)
                redis.publish(channel, dumps({"id": log_line.id}))
        except ConnectionError as e:
            logger.error("Failed to publish log line: %s", e)

    def publish_run_update(self, run: Run):
        try:
            with get_redis() as redis:
                channel = f"build:{run.build.id}:run"
                logger.debug("Publish update for run '%s' on channel '%s'", run.id, channel)
                redis.publish(channel, dumps({"id": run.id}))
        except ConnectionError as e:
            logger.error("Failed to publish run: %s", e)