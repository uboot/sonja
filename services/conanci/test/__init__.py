from conanci import database
from conanci.agent import Agent
from conanci.builder import Builder
from conanci.crawler import Crawler
from conanci.scheduler import Scheduler
from conanci.test.util import create_build, create_channel, create_repo
from contextlib import contextmanager
from unittest.mock import Mock

import os
import time
import unittest

@contextmanager
def environment(key, value):
    os.environ[key] = value
    yield
    del os.environ[key]

class AgentTest(unittest.TestCase):
    def setUp(self):
        self.agent = Agent()
        database.clear_database()

    def tearDown(self):
        self.agent.cancel()
        self.agent.join()

    def test_start(self):
        self.agent.start()

    def test_cancel_and_join(self):
        self.agent.start()
        self.agent.cancel()
        self.agent.join()

    def test_start_build(self):
        with database.session_scope() as session:
            session.add(create_build())
        self.agent.start()
        time.sleep(10)
        with database.session_scope() as session:
            build = session.query(database.Build).first()
            self.assertEqual(build.status, database.BuildStatus.success)

    def test_cancel_build(self):
        with database.session_scope() as session:
            session.add(create_build())
        self.agent.start()
        self.agent.cancel()
        self.agent.join()
        with database.session_scope() as session:
            build = session.query(database.Build).first()
            self.assertEqual(build.status, database.BuildStatus.new)


class CrawlerTest(unittest.TestCase):
    def setUp(self):
        self.scheduler = Mock()
        self.crawler = Crawler(self.scheduler)
        database.clear_database()

    def tearDown(self):
        self.crawler.cancel()
        self.crawler.join()

    def test_start(self):
        self.crawler.start()

    def test_cancel_and_join(self):
        self.crawler.start()
        self.crawler.cancel()
        self.crawler.join()

    def test_start_repo_but_no_channel(self):
        with database.session_scope() as session:
            session.add(create_repo())
        self.crawler.start()
        called = self.crawler.query(lambda: self.scheduler.process_commits.called)
        self.assertFalse(called)

    def test_start_repo_and_channel(self):
        with database.session_scope() as session:
            session.add(create_repo())
            session.add(create_channel())
        self.crawler.start()
        time.sleep(5)
        called = self.crawler.query(lambda: self.scheduler.process_commits.called)
        self.assertTrue(called)


class SchedulerTest(unittest.TestCase):
    def setUp(self):
        self.linux_agent = Mock()
        self.windows_agent = Mock()
        self.scheduler = Scheduler(self.linux_agent, self.windows_agent)
        database.clear_database()

    def tearDown(self):
        self.scheduler.cancel()
        self.scheduler.join()

    def test_start(self):
        self.scheduler.start()


class BuilderTest(unittest.TestCase):
    def test_run_linux(self):
        conan_server = os.environ.get("CONAN_SERVER_URL", "127.0.0.1")
        docker_host = os.environ.get("LINUX_DOCKER_HOST", "")
        with environment("DOCKER_HOST", docker_host), Builder("Linux", "conanio/gcc9:1.29.2") as builder:
            builder.pull()
            builder.setup(conan_server, "agent", "demo")
            with self.assertRaises(Exception):
                builder.run()

    def test_run_windows(self):
        docker_host = os.environ.get("WINDOWS_DOCKER_HOST", "")
        conan_server = os.environ.get("CONAN_SERVER_URL", "127.0.0.1")
        with environment("DOCKER_HOST", docker_host), Builder("Windows", "msvc15:local") as builder:
            builder.pull()
            builder.setup(conan_server, "agent", "demo")
            with self.assertRaises(Exception):
                builder.run()