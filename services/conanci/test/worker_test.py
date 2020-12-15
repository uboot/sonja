from conanci import database
from conanci.agent import Agent
from conanci.crawler import Crawler
from conanci.scheduler import Scheduler
from unittest.mock import Mock

import conanci.test.util as util
import time
import unittest


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
            session.add(util.create_build())
        self.agent.start()
        time.sleep(3)
        with database.session_scope() as session:
            build = session.query(database.Build).first()
            self.assertEqual(build.status, database.BuildStatus.active)

    def test_cancel_build(self):
        with database.session_scope() as session:
            session.add(util.create_build())
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
            session.add(util.create_repo())
        self.crawler.start()
        called = self.crawler.query(lambda: self.scheduler.process_commits.called)
        self.assertFalse(called)

    def test_start_repo_and_channel(self):
        with database.session_scope() as session:
            session.add(util.create_repo())
            session.add(util.create_channel())
        self.crawler.start()
        time.sleep(5)
        called = self.crawler.query(lambda: self.scheduler.process_commits.called)
        self.assertTrue(called)
        with database.session_scope() as session:
            commit = session.query(database.Commit).first()
            self.assertEqual(commit.status, database.CommitStatus.new)

    def test_start_repo_and_old_commits(self):
        with database.session_scope() as session:
            session.add(util.create_commit())
        self.crawler.start()
        time.sleep(5)
        called = self.crawler.query(lambda: self.scheduler.process_commits.called)
        self.assertTrue(called)
        with database.session_scope() as session:
            old_commit = session.query(database.Commit)\
                .filter(database.Commit.status == database.CommitStatus.old)\
                .first()
            self.assertIsNotNone(old_commit)
            new_commit = session.query(database.Commit)\
                .filter(database.Commit.status == database.CommitStatus.new)\
                .first()
            self.assertIsNotNone(new_commit)

    def test_start_invalid_repo(self):
        with database.session_scope() as session:
            session.add(util.create_invalid_repo())
            session.add(util.create_channel())
        self.crawler.start()
        time.sleep(3)
        with database.session_scope() as session:
            commits = session.query(database.Commit).all()
            self.assertEqual(len(commits), 0)


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
