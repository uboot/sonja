from sonja.database import session_scope, reset_database
from sonja.scheduler import Scheduler
from sonja.test import util
from unittest.mock import Mock

import time
import unittest


class TestScheduler(unittest.TestCase):
    def setUp(self):
        self.linux_agent = Mock()
        self.windows_agent = Mock()
        self.redis_client = Mock()
        self.scheduler = Scheduler(self.linux_agent, self.windows_agent, self.redis_client)
        reset_database()

    def tearDown(self):
        self.scheduler.cancel()
        self.scheduler.join()

    def test_start(self):
        self.scheduler.start()

    def test_start_commit_and_profile(self):
        with session_scope() as session:
            session.add(util.create_commit(dict()))
            session.add(util.create_profile(dict()))
        self.scheduler.start()
        time.sleep(1)
        self.scheduler.cancel()
        self.scheduler.join()
        self.assertTrue(self.linux_agent.process_builds.called)
        self.assertTrue(self.windows_agent.process_builds.called)
        self.assertTrue(self.redis_client.publish_build_updates.called)

    def test_start_exclude_repo(self):
        with session_scope() as session:
            session.add(util.create_commit(dict()))
            session.add(util.create_profile({"profile.os": "Windows"}))
        self.scheduler.start()
        time.sleep(1)
        self.scheduler.cancel()
        self.scheduler.join()
        self.assertFalse(self.linux_agent.process_builds.called)
        self.assertFalse(self.windows_agent.process_builds.called)
        self.assertFalse(self.redis_client.publish_build_updates.called)

    def test_start_new_builds(self):
        with session_scope() as session:
            session.add(util.create_build(dict()))
        self.scheduler.start()
        time.sleep(1)
        self.scheduler.cancel()
        self.scheduler.join()
        self.assertTrue(self.linux_agent.process_builds.called)
        self.assertTrue(self.windows_agent.process_builds.called)
        self.assertFalse(self.redis_client.publish_build_updates.called)
