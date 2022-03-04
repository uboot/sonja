import unittest

from sonja import client


@unittest.skip("requires a HTTP server")
class TestLinuxAgent(unittest.TestCase):
    def test_process_builds(self):
        agent = client.LinuxAgent()
        self.assertTrue(agent.process_builds())


@unittest.skip("requires a HTTP server")
class TestWindowsAgent(unittest.TestCase):
    def test_process_builds(self):
        agent = client.WindowsAgent()
        self.assertTrue(agent.process_builds())


@unittest.skip("requires a HTTP server")
class TestScheduler(unittest.TestCase):
    def test_process_commits(self):
        scheduler = client.Scheduler()
        self.assertTrue(scheduler.process_commits())


@unittest.skip("requires a HTTP server")
class TestCrawler(unittest.TestCase):
    def test_process_repo(self):
        crawler = client.Crawler()
        self.assertTrue(crawler.process_repo("1"))
