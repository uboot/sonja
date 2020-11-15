import unittest
from conanci import database
from conanci.agent import Agent
from conanci.config import db
from conanci.test.util import BaseTestCase


class AgentTest(BaseTestCase):
    def setUp(self):
        self.agent = Agent()

    def tearDown(self):
        self.agent.shutdown()
        self.agent = None
        #db.drop_all()

    def test_start(self):
        self.agent.start()

    def test_process_builds(self):
        self.agent.start()
        build = self.createBuild()
        db.session.add(build)
        db.session.commit()

        self.agent.process_builds()

        build = database.Build.query.first()
        self.assertEqual(build.status, database.BuildStatus.active)
