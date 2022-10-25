from sonja.database import session_scope, reset_database
from sonja.model import Run, BuildStatus, RunStatus
from sonja.test import util
from sonja.watchdog import Watchdog
from unittest.mock import Mock
from datetime import datetime

import unittest
import time


class TestWatchdog(unittest.TestCase):
    def setUp(self):
        self.linux_agent = Mock()
        self.windows_agent = Mock()
        self.redis_client = Mock()
        self.watchdog = Watchdog(self.linux_agent, self.windows_agent, self.redis_client)
        reset_database()

    def tearDown(self):
        self.watchdog.cancel()
        self.watchdog.join()

    def test_start(self):
        self.watchdog.start()

    def test_updated_run(self):
        with session_scope() as session:
            session.add(util.create_run({
                "build.status": BuildStatus.active,
                "run.status": RunStatus.active,
                "run.updated": datetime.utcnow()
            }))

        self.watchdog.start()
        time.sleep(1)

        with session_scope() as session:
            run = session.query(Run).first()
            self.assertEqual(BuildStatus.active, run.build.status)
            self.assertEqual(RunStatus.active, run.status)

        self.assertFalse(self.linux_agent.process_builds.called)
        self.assertFalse(self.windows_agent.process_builds.called)
        self.assertFalse(self.redis_client.publish_build_updates.called)

    def test_active_stalled_build(self):
        with session_scope() as session:
            session.add(util.create_run({
                "build.status": BuildStatus.active,
                "run.status": RunStatus.active
            }))

        self.watchdog.start()
        time.sleep(1)

        with session_scope() as session:
            run = session.query(Run).first()
            self.assertEqual(BuildStatus.new, run.build.status)
            self.assertEqual(RunStatus.stalled, run.status)

        self.assertTrue(self.linux_agent.process_builds.called)
        self.assertTrue(self.windows_agent.process_builds.called)
        self.assertTrue(self.redis_client.publish_build_updates.called)

    def test_stopping_stalled_build(self):
        with session_scope() as session:
            session.add(util.create_run({
                "build.status": BuildStatus.stopping,
                "run.status": RunStatus.active
            }))

        self.watchdog.start()
        time.sleep(1)

        with session_scope() as session:
            run = session.query(Run).first()
            self.assertEqual(BuildStatus.stopped, run.build.status)
            self.assertEqual(RunStatus.stalled, run.status)

        self.assertFalse(self.linux_agent.process_builds.called)
        self.assertFalse(self.windows_agent.process_builds.called)
        self.assertTrue(self.redis_client.publish_build_updates.called)

    def test_inactive_run(self):
        with session_scope() as session:
            session.add(util.create_run(dict()))

        self.watchdog.start()
        time.sleep(1)

        with session_scope() as session:
            run = session.query(Run).first()
            self.assertEqual(BuildStatus.new, run.build.status)
            self.assertEqual(RunStatus.active, run.status)

        self.assertFalse(self.linux_agent.process_builds.called)
        self.assertFalse(self.windows_agent.process_builds.called)
        self.assertFalse(self.redis_client.publish_build_updates.called)
