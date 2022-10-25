from sonja.crawler import Crawler
from sonja.database import session_scope, reset_database
from sonja.model import Commit, CommitStatus
from sonja.test import util
from unittest.mock import Mock

import time
import unittest


class TestCrawler(unittest.TestCase):
    def setUp(self):
        self.scheduler = Mock()
        self.crawler = Crawler(self.scheduler)
        reset_database()

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
        with session_scope() as session:
            session.add(util.create_repo(dict()))
        self.crawler.start()
        called = self.crawler.query(lambda: self.scheduler.process_commits.called)
        self.assertFalse(called)

    def test_start_repo_and_channel(self):
        with session_scope() as session:
            session.add(util.create_repo(dict()))
            session.add(util.create_channel(dict()))
        self.crawler.start()
        time.sleep(5)
        called = self.crawler.query(lambda: self.scheduler.process_commits.called)
        self.assertTrue(called)
        with session_scope() as session:
            commit = session.query(Commit).first()
            self.assertEqual(CommitStatus.new, commit.status)

    def test_http_repo(self):
        with session_scope() as session:
            session.add(util.create_repo({"repo.https": True}))
            session.add(util.create_channel(dict()))
        self.crawler.start()
        time.sleep(5)
        called = self.crawler.query(lambda: self.scheduler.process_commits.called)
        self.assertTrue(called)
        with session_scope() as session:
            commit = session.query(Commit).first()
            self.assertEqual(CommitStatus.new, commit.status)

    def test_post_repo(self):
        self.crawler.start()
        time.sleep(1)
        with session_scope() as session:
            session.add(util.create_repo(dict()))
            session.add(util.create_channel(dict()))
        self.crawler.post_repo("1")
        self.crawler.trigger()
        time.sleep(5)
        called = self.crawler.query(lambda: self.scheduler.process_commits.called)
        self.assertTrue(called)
        with session_scope() as session:
            commit = session.query(Commit).first()
            self.assertEqual(CommitStatus.new, commit.status)

    def test_start_repo_and_regex_channel(self):
        with session_scope() as session:
            session.add(util.create_repo(dict()))
            session.add(util.create_channel({"channel.branch": "mai.*"}))
        self.crawler.start()
        time.sleep(5)
        called = self.crawler.query(lambda: self.scheduler.process_commits.called)
        self.assertTrue(called)
        with session_scope() as session:
            commit = session.query(Commit).first()
            self.assertEqual(CommitStatus.new, commit.status)

    def test_start_repo_and_channel_no_match(self):
        with session_scope() as session:
            session.add(util.create_repo(dict()))
            session.add(util.create_channel({"channel.branch": "maste"}))
        self.crawler.start()
        time.sleep(5)
        called = self.crawler.query(lambda: self.scheduler.process_commits.called)
        self.assertFalse(called)

    def test_start_repo_and_old_commits(self):
        with session_scope() as session:
            session.add(util.create_commit({"commit.status": CommitStatus.new}))
        self.crawler.start()
        time.sleep(5)
        called = self.crawler.query(lambda: self.scheduler.process_commits.called)
        self.assertTrue(called)
        with session_scope() as session:
            old_commit = session.query(Commit)\
                .filter(Commit.status == CommitStatus.old)\
                .first()
            self.assertIsNotNone(old_commit)
            new_commit = session.query(Commit)\
                .filter(Commit.status == CommitStatus.new)\
                .first()
            self.assertIsNotNone(new_commit)

    def test_start_invalid_repo(self):
        with session_scope() as session:
            session.add(util.create_repo({"repo.invalid": True}))
            session.add(util.create_channel(dict()))
        self.crawler.start()
        time.sleep(3)
        with session_scope() as session:
            commits = session.query(Commit).all()
            self.assertEqual(len(commits), 0)
