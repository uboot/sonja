from sonja.agent import Agent
from sonja.client import Scheduler
from sonja.redis import RedisClient


agent = Agent(Scheduler(), RedisClient())
