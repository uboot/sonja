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
        reset_database()

    def tearDown(self):
        self.crawler.cancel()
        self.crawler.join()


class TestPeriodicCrawler(TestCrawler):
    def setUp(self):
        super().setUp()
        self.crawler = Crawler(self.scheduler)

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
        self.assertFalse(self.scheduler.process_commits.called)

    def test_start_repo_and_channel(self):
        with session_scope() as session:
            session.add(util.create_repo(dict()))
            session.add(util.create_channel(dict()))
        self.crawler.start()
        self.crawler.try_pause()
        self.assertTrue(self.scheduler.process_commits.called)
        with session_scope() as session:
            commit = session.query(Commit).first()
            self.assertEqual(CommitStatus.new, commit.status)

    def test_http_repo(self):
        with session_scope() as session:
            session.add(util.create_repo({"repo.https": True}))
            session.add(util.create_channel(dict()))
        self.crawler.start()
        self.crawler.try_pause()
        self.assertTrue(self.scheduler.process_commits.called)
        with session_scope() as session:
            commit = session.query(Commit).first()
            self.assertEqual(CommitStatus.new, commit.status)

    def test_start_repo_and_regex_channel(self):
        with session_scope() as session:
            session.add(util.create_repo(dict()))
            session.add(util.create_channel({"channel.ref_pattern": "heads/mai.*"}))
        self.crawler.start()
        self.crawler.try_pause()
        self.assertTrue(self.scheduler.process_commits.called)
        with session_scope() as session:
            commit = session.query(Commit).first()
            self.assertEqual(CommitStatus.new, commit.status)

    def test_start_repo_and_tag_channel(self):
        with session_scope() as session:
            session.add(util.create_repo(dict()))
            session.add(util.create_channel({"channel.ref_pattern": "tags/test-tag"}))
        self.crawler.start()
        self.crawler.try_pause()
        self.assertTrue(self.scheduler.process_commits.called)
        with session_scope() as session:
            commit = session.query(Commit).first()
            self.assertEqual(CommitStatus.new, commit.status)

    def test_start_repo_and_channel_no_match(self):
        with session_scope() as session:
            session.add(util.create_repo(dict()))
            session.add(util.create_channel({"channel.ref_pattern": "heads/maste"}))
        self.crawler.start()
        self.crawler.try_pause()
        self.assertFalse(self.scheduler.process_commits.called)

    def test_start_repo_and_old_commits(self):
        with session_scope() as session:
            session.add(util.create_commit({"commit.status": CommitStatus.new}))
        self.crawler.start()
        self.crawler.try_pause()
        self.assertTrue(self.scheduler.process_commits.called)
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
        self.crawler.try_pause()
        with session_scope() as session:
            commits = session.query(Commit).all()
            self.assertEqual(len(commits), 0)


class TestCrawler(TestCrawler):
    def setUp(self):
        super().setUp()
        self.crawler = Crawler(self.scheduler, periodic=False)

    def test_process_repo(self):
        with session_scope() as session:
            session.add(util.create_repo(dict()))
            session.add(util.create_channel(dict()))
        self.crawler.process_repo("1")
        self.crawler.start()
        self.crawler.try_pause()
        self.assertTrue(self.scheduler.process_commits.called)
        with session_scope() as session:
            commit = session.query(Commit).first()
            self.assertEqual(CommitStatus.new, commit.status)

    def test_process_commit(self):
        with session_scope() as session:
            session.add(util.create_repo(dict()))
            session.add(util.create_channel(dict()))
        self.crawler.process_repo("1", "ad8b2993326cf501b6b5227edd85fc010c9f919d", "heads/main")
        self.crawler.start()
        self.crawler.try_pause()
        self.assertTrue(self.scheduler.process_commits.called)
        with session_scope() as session:
            commit = session.query(Commit).first()
            self.assertEqual(CommitStatus.new, commit.status)
            self.assertEqual("ad8b2993326cf501b6b5227edd85fc010c9f919d", commit.sha)