from conanci import database
from conanci.manager import Manager

import conanci.test.util as util
import unittest

# Requires:
#
# 1. MySQL database
# docker run --rm -d --name mysql -p 3306:3306 -e MYSQL_DATABASE=conan-ci -e MYSQL_ROOT_PASSWORD=secret mysql:8.0.21


class ManagerTest(unittest.TestCase):
    def setUp(self):
        self.manager = Manager()
        database.reset_database()

    def test_start(self):
        with database.session_scope() as session:
            build = util.create_build()
            package = util.create_package({"package.requirement": True})
            build.package = package
            build.missing_packages.append(package)
            build.missing_recipes.append(package.recipe)
            session.add(package)
            session.add(build)

        self.manager.process("")
