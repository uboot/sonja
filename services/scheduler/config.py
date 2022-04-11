from sonja.scheduler import Scheduler
from sonja.client import LinuxAgent, WindowsAgent
from sonja.redis import RedisClient


scheduler = Scheduler(LinuxAgent(), WindowsAgent(), RedisClient())
