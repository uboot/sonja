from sonja.agent import Agent
from sonja.database import session_scope, reset_database
from sonja.model import BuildStatus, Build
from sonja.test import util
from unittest.mock import Mock

import time
import unittest


class TestAgent(unittest.TestCase):
    def setUp(self):
        self.scheduler = Mock()
        self.redis_client = Mock()
        self.agent = Agent(self.scheduler, self.redis_client)
        reset_database()

    def tearDown(self):
        self.agent.cancel()
        self.agent.join()

    def __wait_for_build_status(self, status, timeout):
        start = time.time()
        while True:
            with session_scope() as session:
                build = session.query(Build).first()
                if build.status == status:
                    return build.status
                elif time.time() - start > timeout:
                    return build.status
            time.sleep(1)

    def test_start(self):
        self.agent.start()
        self.assertEqual(self.redis_client.publish_build_update.call_count, 0)
        self.assertEqual(self.redis_client.publish_run_update.call_count, 0)

    def test_cancel_and_join(self):
        self.agent.start()
        self.agent.cancel()
        self.agent.join()
        self.assertEqual(self.redis_client.publish_build_update.call_count, 0)
        self.assertEqual(self.redis_client.publish_run_update.call_count, 0)

    def test_start_build(self):
        with session_scope() as session:
            session.add(util.create_build(dict()))
        self.agent.start()
        self.assertEqual(self.__wait_for_build_status(BuildStatus.active, 15), BuildStatus.active)
        self.assertEqual(self.redis_client.publish_build_update.call_count, 1)
        self.assertEqual(self.redis_client.publish_run_update.call_count, 1)

    def test_complete_build(self):
        with session_scope() as session:
            session.add(util.create_build(dict()))
        self.agent.start()
        self.assertEqual(self.__wait_for_build_status(BuildStatus.success, 15), BuildStatus.success)
        self.assertEqual(self.redis_client.publish_build_update.call_count, 2)
        self.assertEqual(self.redis_client.publish_run_update.call_count, 2)
        self.assertGreater(self.redis_client.publish_log_line_update.call_count, 100)

    def test_complete_build_with_missing_recipe(self):
        with session_scope() as session:
            session.add(util.create_build({
                "repo.dependent": True,
                "ecosystem.empty_remote": True
            }))
        self.agent.start()
        self.assertEqual(self.__wait_for_build_status(BuildStatus.error, 15), BuildStatus.error)
        with session_scope() as session:
            build = session.query(Build).first()
            self.assertEqual(1, len(build.missing_recipes))
        self.assertEqual(self.redis_client.publish_build_update.call_count, 2)
        self.assertEqual(self.redis_client.publish_run_update.call_count, 2)

    def test_complete_build_https(self):
        with session_scope() as session:
            session.add(util.create_build({"repo.https": True}))
        self.agent.start()
        self.assertEqual(self.__wait_for_build_status(BuildStatus.success, 15), BuildStatus.success)
        self.assertEqual(self.redis_client.publish_build_update.call_count, 2)
        self.assertEqual(self.redis_client.publish_run_update.call_count, 2)
        self.assertGreater(self.redis_client.publish_log_line_update.call_count, 100)

    def test_stop_build(self):
        with session_scope() as session:
            build = util.create_build({"repo.deadlock": True})
            session.add(build)
        self.agent.start()
        self.__wait_for_build_status(BuildStatus.active, 15)
        with session_scope() as session:
            build = session.query(Build).first()
            build.status = BuildStatus.stopping
        self.assertEqual(self.__wait_for_build_status(BuildStatus.stopped, 15), BuildStatus.stopped)
        self.assertEqual(self.redis_client.publish_build_update.call_count, 2)
        self.assertEqual(self.redis_client.publish_run_update.call_count, 2)

    def test_cancel_build(self):
        with session_scope() as session:
            session.add(util.create_build(dict()))
        self.agent.start()
        self.__wait_for_build_status(BuildStatus.active, 15)
        self.agent.cancel()
        self.agent.join()
        self.assertEqual(self.__wait_for_build_status(BuildStatus.new, 15), BuildStatus.new)
        self.assertEqual(self.redis_client.publish_build_update.call_count, 2)
        self.assertEqual(self.redis_client.publish_run_update.call_count, 2)
