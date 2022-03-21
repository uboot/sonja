from sonja import database
from sonja.agent import Agent
from sonja.crawler import Crawler
from sonja.scheduler import Scheduler
from unittest.mock import Mock

from sonja.test import util
import time
import unittest

# Requires:
#
# 1. MySQL database
# docker run --rm -d --name mysql -p 3306:3306 -e MYSQL_DATABASE=sonja -e MYSQL_ROOT_PASSWORD=secret mysql:8.0.21


class TestAgent(unittest.TestCase):
    def setUp(self):
        self.scheduler = Mock()
        self.agent = Agent(self.scheduler)
        database.reset_database()

    def tearDown(self):
        self.agent.cancel()
        self.agent.join()

    def __wait_for_build_status(self, status, timeout):
        start = time.time()
        while True:
            with database.session_scope() as session:
                build = session.query(database.Build).first()
                if build.status == status:
                    return build.status
                elif time.time() - start > timeout:
                    return build.status
            time.sleep(1)

    def test_start(self):
        self.agent.start()

    def test_cancel_and_join(self):
        self.agent.start()
        self.agent.cancel()
        self.agent.join()

    def test_start_build(self):
        with database.session_scope() as session:
            session.add(util.create_build(dict()))
        self.agent.start()
        self.assertEquals(self.__wait_for_build_status(database.BuildStatus.active, 15), database.BuildStatus.active)

    def test_complete_build(self):
        with database.session_scope() as session:
            session.add(util.create_build(dict()))
        self.agent.start()
        self.assertEquals(self.__wait_for_build_status(database.BuildStatus.success, 15), database.BuildStatus.success)

    def test_complete_build_with_dependency(self):
        with database.session_scope() as session:
            session.add(util.create_build({
                "repo.dependent": True,
                "ecosystem.empty_remote": True
            }))
        self.agent.start()
        self.assertEquals(self.__wait_for_build_status(database.BuildStatus.error, 15), database.BuildStatus.error)
        with database.session_scope() as session:
            build = session.query(database.Build).first()
            self.assertEquals(1, len(build.missing_recipes))

    def test_complete_build_https(self):
        with database.session_scope() as session:
            session.add(util.create_build({"repo.https": True}))
        self.agent.start()
        self.assertEquals(self.__wait_for_build_status(database.BuildStatus.success, 15), database.BuildStatus.success)

    def test_stop_build(self):
        with database.session_scope() as session:
            build = util.create_build({"repo.deadlock": True})
            session.add(build)
        self.agent.start()
        self.__wait_for_build_status(database.BuildStatus.active, 15)
        with database.session_scope() as session:
            build = session.query(database.Build).first()
            build.status = database.BuildStatus.stopping
        self.assertEqual(self.__wait_for_build_status(database.BuildStatus.stopped, 15), database.BuildStatus.stopped)

    def test_cancel_build(self):
        with database.session_scope() as session:
            session.add(util.create_build(dict()))
        self.agent.start()
        self.__wait_for_build_status(database.BuildStatus.active, 15)
        self.agent.cancel()
        self.agent.join()
        self.assertEquals(self.__wait_for_build_status(database.BuildStatus.new, 15), database.BuildStatus.new)


class TestCrawler(unittest.TestCase):
    def setUp(self):
        self.scheduler = Mock()
        self.crawler = Crawler(self.scheduler)
        database.reset_database()

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
            session.add(util.create_repo(dict()))
        self.crawler.start()
        called = self.crawler.query(lambda: self.scheduler.process_commits.called)
        self.assertFalse(called)

    def test_start_repo_and_channel(self):
        with database.session_scope() as session:
            session.add(util.create_repo(dict()))
            session.add(util.create_channel(dict()))
        self.crawler.start()
        time.sleep(5)
        called = self.crawler.query(lambda: self.scheduler.process_commits.called)
        self.assertTrue(called)
        with database.session_scope() as session:
            commit = session.query(database.Commit).first()
            self.assertEqual(database.CommitStatus.new, commit.status)

    def test_http_repo(self):
        with database.session_scope() as session:
            session.add(util.create_repo({"repo.https": True}))
            session.add(util.create_channel(dict()))
        self.crawler.start()
        time.sleep(5)
        called = self.crawler.query(lambda: self.scheduler.process_commits.called)
        self.assertTrue(called)
        with database.session_scope() as session:
            commit = session.query(database.Commit).first()
            self.assertEqual(database.CommitStatus.new, commit.status)

    def test_post_repo(self):
        self.crawler.start()
        time.sleep(1)
        with database.session_scope() as session:
            session.add(util.create_repo(dict()))
            session.add(util.create_channel(dict()))
        self.crawler.post_repo("1")
        self.crawler.trigger()
        time.sleep(5)
        called = self.crawler.query(lambda: self.scheduler.process_commits.called)
        self.assertTrue(called)
        with database.session_scope() as session:
            commit = session.query(database.Commit).first()
            self.assertEqual(database.CommitStatus.new, commit.status)

    def test_start_repo_and_regex_channel(self):
        with database.session_scope() as session:
            session.add(util.create_repo(dict()))
            session.add(util.create_channel({"channel.branch": "mai.*"}))
        self.crawler.start()
        time.sleep(5)
        called = self.crawler.query(lambda: self.scheduler.process_commits.called)
        self.assertTrue(called)
        with database.session_scope() as session:
            commit = session.query(database.Commit).first()
            self.assertEqual(database.CommitStatus.new, commit.status)

    def test_start_repo_and_channel_no_match(self):
        with database.session_scope() as session:
            session.add(util.create_repo(dict()))
            session.add(util.create_channel({"channel.branch": "maste"}))
        self.crawler.start()
        time.sleep(5)
        called = self.crawler.query(lambda: self.scheduler.process_commits.called)
        self.assertFalse(called)

    def test_start_repo_and_old_commits(self):
        with database.session_scope() as session:
            session.add(util.create_commit({"commit.status": database.CommitStatus.new}))
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
            session.add(util.create_repo({"repo.invalid": True}))
            session.add(util.create_channel(dict()))
        self.crawler.start()
        time.sleep(3)
        with database.session_scope() as session:
            commits = session.query(database.Commit).all()
            self.assertEqual(len(commits), 0)


class TestScheduler(unittest.TestCase):
    def setUp(self):
        self.linux_agent = Mock()
        self.windows_agent = Mock()
        self.scheduler = Scheduler(self.linux_agent, self.windows_agent)
        database.reset_database()

    def tearDown(self):
        self.scheduler.cancel()
        self.scheduler.join()

    def test_start(self):
        self.scheduler.start()

    def test_start_commit_and_profile(self):
        with database.session_scope() as session:
            session.add(util.create_commit(dict()))
            session.add(util.create_profile(dict()))
        self.scheduler.start()
        time.sleep(1)
        self.scheduler.cancel()
        self.scheduler.join()
        self.assertTrue(self.linux_agent.process_builds.called)
        self.assertTrue(self.windows_agent.process_builds.called)

    def test_start_exclude_repo(self):
        with database.session_scope() as session:
            session.add(util.create_commit(dict()))
            session.add(util.create_profile({"profile.os": "Windows"}))
        self.scheduler.start()
        time.sleep(1)
        self.scheduler.cancel()
        self.scheduler.join()
        self.assertFalse(self.linux_agent.process_builds.called)
        self.assertFalse(self.windows_agent.process_builds.called)

    def test_start_new_builds(self):
        with database.session_scope() as session:
            session.add(util.create_build(dict()))
        self.scheduler.start()
        time.sleep(1)
        self.scheduler.cancel()
        self.scheduler.join()
        self.assertTrue(self.linux_agent.process_builds.called)
        self.assertTrue(self.windows_agent.process_builds.called)
