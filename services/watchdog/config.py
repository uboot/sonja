from sonja.watchdog import Watchdog
from sonja.client import LinuxAgent, WindowsAgent
from sonja.redis import RedisClient


watchdog = Watchdog(LinuxAgent(), WindowsAgent(), RedisClient())
