import unittest

from sonja import database, model
from sonja import demo


class TestDemo(unittest.TestCase):
    def setUp(self):
        database.reset_database()

    def test_populate_initial_data(self):
        database.create_initial_ecosystem("Ecosystem")
        database.create_initial_configuration()
        demo.populate_initial_data(1)
        with database.session_scope() as session:
            repos = session.query(model.Repo).all()
            self.assertEqual(5, len(repos))
            ecosystem = session.query(model.Ecosystem).first()
            self.assertEqual("mycompany", ecosystem.user)
            configuration = session.query(model.Configuration).first()
            self.assertEqual(540, len(configuration.known_hosts))
            self.assertEqual(1, len(configuration.docker_credentials))

    def test_populate_ecosystem(self):
        database.create_initial_ecosystem("Ecosystem")
        demo.populate_ecosystem()
        with database.session_scope() as session:
            repos = session.query(model.Repo).all()
            self.assertEqual(5, len(repos))
