import unittest

from sonja import database
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

    def test_create_package_with_requirement(self):
        with database.session_scope() as session:
            package_1 = util.create_package(dict())
            package_2 = util.create_package(dict())
            package_1.requires = [package_2]
            self.assertEqual(1, len(package_2.required_by))

    def test_create_recipe_revision(self):
        with database.session_scope() as session:
            recipe_revision = util.create_recipe_revision(dict())
            self.assertIsNotNone(recipe_revision.recipe)
            self.assertEqual(1, len(recipe_revision.recipe.revisions))

    def test_create_recipe_revision_with_build(self):
        with database.session_scope() as session:
            recipe_revision = util.create_recipe_revision(dict())
            build = util.create_build(dict())
            build.recipe_revision = recipe_revision
            session.commit()
            self.assertIsNotNone(recipe_revision.builds)
            self.assertEqual(1, len(recipe_revision.builds))

    def test_create_recipe_with_current_revision(self):
        with database.session_scope() as session:
            recipe = util.create_recipe(dict())
            recipe_revision = database.RecipeRevision()
            recipe_revision.recipe = recipe
            recipe.current_revision = recipe_revision
            session.commit()

            self.assertIsNotNone(recipe_revision.recipe)
            self.assertEqual(1, len(recipe_revision.recipe.revisions))

    def test_delete_recipe_with_current_revision(self):
        with database.session_scope() as session:
            recipe = util.create_recipe(dict())
            recipe_revision = database.RecipeRevision()
            recipe_revision.recipe = recipe
            recipe.current_revision = recipe_revision
            session.add(recipe)
            session.commit()
            session.delete(recipe)

    def test_update_recipe_with_current_revision(self):
        with database.session_scope() as session:
            recipe = util.create_recipe(dict())
            recipe_revision = database.RecipeRevision()
            recipe_revision.recipe = recipe
            recipe.current_revision = recipe_revision
            session.add(recipe)
            session.commit()
            recipe_revision = database.RecipeRevision()
            recipe_revision.recipe = recipe
            recipe.current_revision = recipe_revision
            session.commit()
