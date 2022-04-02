import unittest

from sonja import database
from sonja import demo
from sonja.test import util


class TestDatabase(unittest.TestCase):
    def setUp(self):
        database.reset_database()

    def test_create_initial_user(self):
        database.create_initial_user("user", "password")
        with database.session_scope() as session:
            users = session.query(database.User).all()
            self.assertEqual(len(users), 1)

    def test_create_initial_user_twice(self):
        database.create_initial_user("user1", "password")
        database.create_initial_user("user2", "password")
        with database.session_scope() as session:
            users = session.query(database.User).all()
            self.assertEqual(len(users), 1)

    def test_create_initial_ecosystem(self):
        self.assertEqual(database.create_initial_ecosystem("Ecosystem"), 1)
        with database.session_scope() as session:
            ecosystems = session.query(database.Ecosystem).all()
            self.assertEqual(len(ecosystems), 1)

    def test_create_initial_ecosystem_twice(self):
        self.assertEqual(database.create_initial_ecosystem("Ecosystem"), 1)
        self.assertEqual(database.create_initial_ecosystem("Ecosystem"), 0)
        with database.session_scope() as session:
            ecosystems = session.query(database.Ecosystem).all()
            self.assertEqual(len(ecosystems), 1)

    def test_add_demo_data_to_ecosystem(self):
        database.create_initial_ecosystem("Ecosystem")
        demo.add_demo_data_to_ecosystem(1)
        with database.session_scope() as session:
            repos = session.query(database.Repo).all()
            self.assertEqual(len(repos), 12)

    def test_remove_but_last_user_last_user(self):
        with database.session_scope() as session:
            user = database.User()
            user.user_name = "user"
            session.add(user)

        with database.session_scope() as session:
            self.assertRaises(database.OperationFailed, lambda: database.remove_but_last_user(session, "1"))

        with database.session_scope() as session:
            user = session.query(database.User).filter_by(id="1").first()
            self.assertIsNotNone(user)

    def test_remove_but_last_user(self):
        with database.session_scope() as session:
            user1 = database.User()
            user2 = database.User()
            user1.user_name = "user1"
            user2.user_name = "user2"
            session.add(user1)
            session.add(user2)

        # should not raise an exception
        with database.session_scope() as session:
            database.remove_but_last_user(session, "1")

        with database.session_scope() as session:
            num_users = session.query(database.User).count()
            self.assertEqual(num_users, 1)

    def test_create_build_with_missing_package(self):
        with database.session_scope() as session:
            build = util.create_build(dict())
            package = util.create_package(dict())
            build.missing_packages = [package]
            session.add(build)

        with database.session_scope() as session:
            num_packages = session.query(database.Package).count()
            self.assertEqual(1, num_packages)

    def test_create_build_with_missing_recipe(self):
        with database.session_scope() as session:
            build = util.create_build(dict())
            recipe = util.create_recipe(dict())
            build.missing_recipes = [recipe]
            session.add(build)

        with database.session_scope() as session:
            num_recipes = session.query(database.Recipe).count()
            self.assertEqual(1, num_recipes)
