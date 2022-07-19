from sonja.manager import Manager
from sonja.database import session_scope, reset_database
from sonja.model import BuildStatus, Build, Recipe, RecipeRevision, Package
from unittest.mock import Mock

import sonja.test.util as util
import os
import unittest


def _setup_build_output(create_file="create.json", info_file="info.json"):
    build_output = dict()
    output_files = {
        "create": create_file,
        "info": info_file
    }

    for output in output_files:
        output_file = os.path.join(os.path.dirname(__file__), "data/{0}".format(output_files[output]))
        with open(output_file) as f:
            build_output[output] = f.read()

    return build_output


def _create_waiting_build(session, ecosystem, missing_packages=[], missing_recipes=[]):
    build = util.create_build({"ecosystem": ecosystem})
    build.status = BuildStatus.error
    build.missing_packages = missing_packages
    build.missing_recipes = missing_recipes
    session.add(build)
    session.commit()
    return build.id


def _create_build(session, ecosystem):
    build = util.create_build({"ecosystem": ecosystem})
    session.add(build)
    session.commit()
    return build.id


class TestManager(unittest.TestCase):
    def setUp(self):
        reset_database()
        self.redis_client = Mock()
        self.manager = Manager(self.redis_client)

    def test_process_success(self):
        build_output = _setup_build_output()

        with session_scope() as session:
            build = util.create_build(dict())
            session.add(build)
            session.commit()
            build_id = build.id

        result = self.manager.process_success(build_id, build_output)

        self.assertFalse("new_builds" in result.keys())

        with session_scope() as session:
            build = session.query(Build).filter_by(id=build_id).first()
            self.assertIsNotNone(build.package)
            self.assertEqual("227220812d7ea3aa060187bae41abbc9911dfdfd", build.package.package_id)
            self.assertEqual("app", build.package.recipe_revision.recipe.name)
            self.assertEqual("2b44d2dde63878dd279ebe5d38c60dfaa97153fb", build.package.recipe_revision.revision)
            self.assertEqual(1, len(build.package.requires))

    def test_process_success_required_by(self):
        build_output = _setup_build_output()

        with session_scope() as session:
            ecosystem = util.create_ecosystem(dict())
            dependency = util.create_build({
                "ecosystem": ecosystem,
            })
            package = util.create_package({
                "ecosystem": ecosystem,
                "package.package_id": "05b9eeef9ae43a8780565a51d60b777370566d07",
                "recipe_revision.revision": "2b44d2dde63878dd279ebe5d38c60dfaa97153fb",
                "recipe.name": "hello"
            })
            dependency.package = package
            session.add(dependency)
            build = util.create_build({
                "ecosystem": ecosystem,
                "repo.dependent": True
            })
            session.add(build)
            session.commit()
            dependency_id = dependency.id
            build_id = build.id

        result = self.manager.process_success(build_id, build_output)

        self.assertFalse("new_builds" in result.keys())

        with session_scope() as session:
            build = session.query(Build).filter_by(id=build_id).first()
            dependency = session.query(Build).filter_by(id=dependency_id).first()
            self.assertIsNotNone(build.package)
            self.assertEqual("227220812d7ea3aa060187bae41abbc9911dfdfd", build.package.package_id)
            self.assertEqual("app", build.package.recipe_revision.recipe.name)
            self.assertEqual("2b44d2dde63878dd279ebe5d38c60dfaa97153fb", build.package.recipe_revision.revision)
            self.assertEqual(1, len(build.package.requires))
            self.assertEqual(1, len(dependency.package.required_by))
            self.assertEqual(dependency.package.id, build.package.requires[0].id)
            self.assertEqual(build.package.id, dependency.package.required_by[0].id)

    def test_process_success_existing_recipe(self):
        build_output = _setup_build_output()

        with session_scope() as session:
            parameters = dict()
            recipe = util.create_recipe(parameters)
            session.add(recipe)
            build = util.create_build(parameters)
            session.add(build)
            session.commit()
            build_id = build.id

        self.manager.process_success(build_id, build_output)

        with session_scope() as session:
            build = session.query(Build).filter_by(id=build_id).first()
            recipes = session.query(Recipe).all()
            recipe_revisions = session.query(RecipeRevision).all()
            self.assertEqual(2, len(recipes))
            self.assertEqual(2, len(recipe_revisions))
            self.assertEqual(1, build.package.recipe_revision.id)

    def test_process_success_existing_recipe_revision(self):
        build_output = _setup_build_output()

        with session_scope() as session:
            parameters = dict()
            recipe = util.create_recipe_revision(parameters)
            session.add(recipe)
            build = util.create_build(parameters)
            session.add(build)
            session.commit()
            build_id = build.id

        self.manager.process_success(build_id, build_output)

        with session_scope() as session:
            build = session.query(Build).filter_by(id=build_id).first()
            recipes = session.query(Recipe).all()
            recipe_revisions = session.query(RecipeRevision).all()
            self.assertEqual(2, len(recipes))
            self.assertEqual(2, len(recipe_revisions))
            self.assertEqual(1, build.package.recipe_revision.id)

    def test_process_success_existing_package(self):
        build_output = _setup_build_output()

        with session_scope() as session:
            parameters = dict()
            package = util.create_package(parameters)
            session.add(package)
            build = util.create_build(parameters)
            session.add(build)
            session.commit()
            build_id = build.id

        self.manager.process_success(build_id, build_output)

        with session_scope() as session:
            build = session.query(Build).filter_by(id=build_id).first()
            packages = session.query(Package).all()
            self.assertEqual(2, len(packages))
            self.assertEqual(1, build.package.id)

    def test_process_failure_missing_package(self):
        build_output = _setup_build_output("create_missing_package.json")

        with session_scope() as session:
            build = util.create_build(dict())
            session.add(build)
            session.commit()
            build_id = build.id

        self.manager.process_failure(build_id, build_output)

        with session_scope() as session:
            # a recipe for the failed build should exist
            recipe = session.query(Recipe).filter_by(name="hello").first()
            self.assertIsNotNone(recipe)
            recipe_revision = session.query(RecipeRevision).\
                filter_by(recipe_id=recipe.id, revision="f5c1ba6f1af634f500f7e0255619fecf4777965f")
            self.assertIsNotNone(recipe_revision)

            # the build should now have a missing package
            build = session.query(Build).filter_by(id=build_id).first()
            self.assertEqual(1, len(build.missing_packages))
            package = build.missing_packages[0]
            self.assertEqual("d057732059ea44a47760900cb5e4855d2bea8714", package.package_id)

            recipe_revision = package.recipe_revision
            self.assertIsNotNone(recipe_revision)
            self.assertEqual("f5c1ba6f1af634f500f7e0255619fecf4777965f", recipe_revision.revision)

            recipe = recipe_revision.recipe
            self.assertIsNotNone(recipe)
            self.assertEqual("base", recipe.name)
            self.assertEqual("1.2.3", recipe.version)
            self.assertEqual("mycompany", recipe.user)
            self.assertEqual("stable", recipe.channel)

    def test_process_failure_missing_package_no_revision(self):
        build_output = _setup_build_output("create_missing_package_no_revision.json")

        with session_scope() as session:
            build = util.create_build(dict())
            session.add(build)
            session.commit()
            build_id = build.id

        self.manager.process_failure(build_id, build_output)

        with session_scope() as session:
            build = session.query(Build).filter_by(id=build_id).first()
            self.assertEqual(1, len(build.missing_packages))
            recipe_revision = build.missing_packages[0].recipe_revision
            self.assertIsNotNone(recipe_revision)
            self.assertEqual("", recipe_revision.revision)

    def test_process_failure_missing_package_twice(self):
        build_output_missing_package = _setup_build_output("create_missing_package.json")
        build_output_missing_recipe = _setup_build_output("create_missing_recipe.json")

        with session_scope() as session:
            build = util.create_build(dict())
            session.add(build)
            session.commit()
            build_id = build.id

        self.manager.process_failure(build_id, build_output_missing_package)
        self.manager.process_failure(build_id, build_output_missing_recipe)

        with session_scope() as session:
            build = session.query(Build).filter_by(id=build_id).first()
            self.assertEqual(0, len(build.missing_packages))
            self.assertEqual(1, len(build.missing_recipes))

    def test_process_failure_missing_recipe(self):
        build_output = _setup_build_output("create_missing_recipe.json")

        with session_scope() as session:
            build = util.create_build(dict())
            session.add(build)
            session.commit()
            build_id = build.id

        self.manager.process_failure(build_id, build_output)

        with session_scope() as session:
            # a recipe for the failed build should exist
            recipe = session.query(Recipe).filter_by(name="hello").first()
            self.assertIsNotNone(recipe)
            recipe_revision = session.query(RecipeRevision).\
                filter_by(recipe_id=recipe.id, revision="f5c1ba6f1af634f500f7e0255619fecf4777965f")
            self.assertIsNotNone(recipe_revision)

            # the build should now have a missing recipe
            build = session.query(Build).filter_by(id=build_id).first()
            self.assertEqual(1, len(build.missing_recipes))
            recipe = build.missing_recipes[0]
            self.assertEqual("base", recipe.name)
            self.assertEqual("1.2.3", recipe.version)
            self.assertEqual("mycompany", recipe.user)
            self.assertEqual("stable", recipe.channel)

    def test_process_success_remove_missing_items(self):
        build_output = _setup_build_output("create.json")

        with session_scope() as session:
            build = util.create_build(dict())
            build.missing_recipes = [util.create_recipe(dict())]
            build.missing_packages = [util.create_package(dict())]
            session.add(build)
            session.commit()
            build_id = build.id

        self.manager.process_success(build_id, build_output)

        with session_scope() as session:
            build = session.query(Build).filter_by(id=build_id).first()
            self.assertEqual(0, len(build.missing_recipes))
            self.assertEqual(0, len(build.missing_packages))

    def test_process_success_waiting_for_recipe(self):
        build_output = _setup_build_output("create.json")

        with session_scope() as session:
            ecosystem = util.create_ecosystem(dict())
            waiting_build_id = _create_waiting_build(session, ecosystem,
                                                     missing_recipes=[util.create_recipe({"ecosystem": ecosystem})])
            build_id = _create_build(session, ecosystem)

        result = self.manager.process_success(build_id, build_output)

        self.assertTrue(result["new_builds"])

        with session_scope() as session:
            waiting_build = session.query(Build).filter_by(id=waiting_build_id).first()
            self.assertEqual(BuildStatus.new, waiting_build.status)

    def test_process_success_waiting_for_package(self):
        build_output = _setup_build_output("create.json")
        with session_scope() as session:
            ecosystem = util.create_ecosystem(dict())
            waiting_build_id = _create_waiting_build(session, ecosystem,
                                                     missing_packages=[util.create_package({"ecosystem": ecosystem})])
            build_id = _create_build(session, ecosystem)

        result = self.manager.process_success(build_id, build_output)

        self.assertTrue(result["new_builds"])

        with session_scope() as session:
            waiting_build = session.query(Build).filter_by(id=waiting_build_id).first()
            self.assertEqual(BuildStatus.new, waiting_build.status)

        self.assertTrue(self.redis_client.publish_build_updates.called)

    def test_process_success_waiting_for_package_no_revision(self):
        build_output = _setup_build_output("create.json")
        with session_scope() as session:
            ecosystem = util.create_ecosystem(dict())
            waiting_build_id = _create_waiting_build(session, ecosystem, missing_packages=[util.create_package(
                {
                    "ecosystem": ecosystem,
                    "recipe_revision.revision": ""
                })
            ])
            build_id = _create_build(session, ecosystem)

        result = self.manager.process_success(build_id, build_output)

        self.assertTrue(result["new_builds"])

        with session_scope() as session:
            waiting_build = session.query(Build).filter_by(id=waiting_build_id).first()
            self.assertEqual(BuildStatus.new, waiting_build.status)

        self.assertTrue(self.redis_client.publish_build_updates.called)

    def test_process_success_waiting_for_package_different_revision(self):
        build_output = _setup_build_output("create.json")
        with session_scope() as session:
            ecosystem = util.create_ecosystem(dict())
            waiting_build_id = _create_waiting_build(session, ecosystem, missing_packages=[util.create_package(
                {
                    "ecosystem": ecosystem,
                    "recipe_revision.revision": "f5c1ba6f1af634f500f7e0255619fecf4777965f"
                })
            ])
            build_id = _create_build(session, ecosystem)

        result = self.manager.process_success(build_id, build_output)

        self.assertTrue(result["new_builds"])

        with session_scope() as session:
            waiting_build = session.query(Build).filter_by(id=waiting_build_id).first()
            self.assertEqual(BuildStatus.new, waiting_build.status)

        self.assertTrue(self.redis_client.publish_build_updates.called)

    def test_process_success_waiting_for_package_different_package_id(self):
        build_output = _setup_build_output("create.json")
        with session_scope() as session:
            ecosystem = util.create_ecosystem(dict())
            waiting_build_id = _create_waiting_build(session, ecosystem, missing_packages=[util.create_package(
                {
                    "ecosystem": ecosystem,
                    "package.package_id": "d057732059ea44a47760900cb5e4855d2bea8714"
                })
            ])
            build_id = _create_build(session, ecosystem)

        result = self.manager.process_success(build_id, build_output)

        self.assertFalse("new_builds" in result.keys())

        with session_scope() as session:
            waiting_build = session.query(Build).filter_by(id=waiting_build_id).first()
            self.assertEqual(BuildStatus.error, waiting_build.status)
