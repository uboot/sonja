import unittest
from conanci import database
from conanci.agent import Agent
from conanci.config import db
from conanci.test.util import BaseTestCase


class AgentTest(BaseTestCase):
    def setUp(self):
        self.agent = Agent()
        db.drop_all()
        db.create_all()

    def test_process_builds(self):
        build = self.createBuild()
        db.session.add(build)
        db.session.commit()

        self.agent.process_builds()
        build = database.Build.query.first()
        self.assertEqual(build.status, database.BuildStatus.active)
