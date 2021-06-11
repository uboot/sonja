from conanci import database, manager

import conanci.test.util as util
import os
import unittest

# Requires:
#
# 1. MySQL database
# docker run --rm -d --name mysql -p 3306:3306 -e MYSQL_DATABASE=conan-ci -e MYSQL_ROOT_PASSWORD=secret mysql:8.0.21

def _setup_build_output():
    build_output = dict()
    create_output_file = os.path.join(os.path.dirname(__file__), "create.json")
    with open(create_output_file) as f:
        build_output["create"] = f.read()
    return build_output


class ManagerTest(unittest.TestCase):
    def setUp(self):
        database.reset_database()

    def test_process(self):
        build_output = _setup_build_output()

        with database.session_scope() as session:
            build = util.create_build(dict())
            session.add(build)
            session.commit()
            build_id = build.id

        manager.process(build_id, build_output)

        with database.session_scope() as session:
            build = session.query(database.Build).filter_by(id=build_id).first()
            self.assertIsNotNone(build.package)
            self.assertEqual("227220812d7ea3aa060187bae41abbc9911dfdfd", build.package.package_id)
            self.assertEqual("app", build.package.recipe_revision.recipe.name)
            self.assertEqual("2b44d2dde63878dd279ebe5d38c60dfaa97153fb", build.package.recipe_revision.revision)

    def test_process_existing_recipe(self):
        build_output = _setup_build_output()

        with database.session_scope() as session:
            parameters = dict()
            recipe = util.create_recipe(parameters)
            session.add(recipe)
            build = util.create_build(parameters)
            session.add(build)
            session.commit()
            build_id = build.id

        manager.process(build_id, build_output)

        with database.session_scope() as session:
            build = session.query(database.Build).filter_by(id=build_id).first()
            recipes = session.query(database.Recipe).all()
            recipe_revisions = session.query(database.RecipeRevision).all()
            self.assertEqual(1, len(recipes))
            self.assertEqual(1, len(recipe_revisions))
            self.assertEqual(1, build.package.recipe_revision.id)

    def test_process_existing_recipe_revision(self):
        build_output = _setup_build_output()

        with database.session_scope() as session:
            parameters = dict()
            recipe = util.create_recipe_revision(parameters)
            session.add(recipe)
            build = util.create_build(parameters)
            session.add(build)
            session.commit()
            build_id = build.id

        manager.process(build_id, build_output)

        with database.session_scope() as session:
            build = session.query(database.Build).filter_by(id=build_id).first()
            recipes = session.query(database.Recipe).all()
            recipe_revisions = session.query(database.RecipeRevision).all()
            self.assertEqual(1, len(recipes))
            self.assertEqual(1, len(recipe_revisions))
            self.assertEqual(1, build.package.recipe_revision.id)

    def test_process_existing_package(self):
        build_output = _setup_build_output()

        with database.session_scope() as session:
            parameters = dict()
            package = util.create_package(parameters)
            session.add(package)
            build = util.create_build(parameters)
            session.add(build)
            session.commit()
            build_id = build.id

        manager.process(build_id, build_output)

        with database.session_scope() as session:
            build = session.query(database.Build).filter_by(id=build_id).first()
            packages = session.query(database.Package).all()
            self.assertEqual(1, len(packages))
            self.assertEqual(1, build.package.id)
