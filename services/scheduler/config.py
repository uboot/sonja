from sonja.scheduler import Scheduler
from sonja.client import LinuxAgent, WindowsAgent


scheduler = Scheduler(LinuxAgent(), WindowsAgent())
