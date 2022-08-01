import unittest

from sonja import database
from sonja import demo


class TestDemo(unittest.TestCase):
    def setUp(self):
        database.reset_database()

    def test_add_demo_data_to_ecosystem(self):
        database.create_initial_ecosystem("Ecosystem")
        demo.add_demo_data_to_ecosystem(1)
        with database.session_scope() as session:
            repos = session.query(database.Repo).all()
            self.assertEqual(len(repos), 20)
