import unittest

from sonja import client


class TestLinuxAgent(unittest.TestCase):
    def test_process_builds(self):
        agent = client.LinuxAgent()
        self.assertTrue(agent.process_builds())


class TestWindowsAgent(unittest.TestCase):
    def test_process_builds(self):
        agent = client.WindowsAgent()
        self.assertTrue(agent.process_builds())


class TestScheduler(unittest.TestCase):
    def test_process_commits(self):
        scheduler = client.Scheduler()
        self.assertTrue(scheduler.process_commits())


class TestCrawler(unittest.TestCase):
    def test_process_repo(self):
        crawler = client.Crawler()
        self.assertTrue(crawler.process_repo("1"))
