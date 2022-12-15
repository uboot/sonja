from sonja.client import Crawler, LinuxAgent, WindowsAgent
from sonja.redis import RedisClient

crawler = Crawler()
linuxAgent = LinuxAgent()
windowsAgent = WindowsAgent()
redisClient = RedisClient()


def get_crawler() -> Crawler:
    return crawler


def get_linux_agent() -> LinuxAgent:
    return linuxAgent


def get_windows_agent() -> WindowsAgent:
    return windowsAgent


def get_redis_client() -> RedisClient:
    return redisClient