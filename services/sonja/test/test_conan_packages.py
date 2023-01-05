from sonja import database
from sonja.agent import Agent
from unittest.mock import Mock

import os
import time
import unittest

from sonja.model import ConanCredential


@unittest.skip("building packages can take very long")
class TestConanPackages(unittest.TestCase):
    def setUp(self):
        database.reset_database()
        self.scheduler = Mock()
        self.agent = Agent(self.scheduler)

    def tearDown(self):
        self.agent.cancel()
        self.agent.join()

    def __setup_build(self, **params):
        with database.session_scope() as session:
            ecosystem = database.Ecosystem()
            ecosystem.name = "My Ecosystem"
            ecosystem.user = "sonja"
            ecosystem.conan_config_url = "https://github.com/uboot/conan-config.git"
            ecosystem.conan_config_path = "default"
            ecosystem.conan_config_branch = ""
            conan_credential = ConanCredential()
            conan_credential.remote = "uboot"
            conan_credential.username = "agent"
            conan_credential.password = os.environ.get("CONAN_PASSWORD", "")
            self.__ecosystem.conan_credentials = [conan_credential]

            repo = database.Repo()
            repo.name = "My Repo"
            repo.url = params["url"]
            repo.path = params["path"]
            repo.version = params["version"]
            repo.ecosystem = ecosystem

            channel = database.Channel()
            channel.name = "channel"
            channel.conan_channel = "latest"
            channel.conan_remote = "uboot"
            channel.ecosystem = ecosystem

            commit = database.Commit()
            commit.sha = params["sha"]
            commit.repo = repo
            commit.channel = channel
            commit.status = database.CommitStatus.new

            profile = database.Profile()
            profile.name = "Profile"
            profile.platform = database.Platform.linux
            profile.conan_profile = "linux-release"
            profile.container = "uboot/gcc9:latest"
            profile.ecosystem = ecosystem

            log = database.Log()
            log.logs = ""

            build = database.Build()
            build.status = database.BuildStatus.new
            build.commit = commit
            build.profile = profile
            build.log = log

            session.add(build)

    def __wait_for_build_status(self, status, timeout):
        start = time.time()
        while True:
            with database.session_scope() as session:
                build = session.query(database.Build).first()
                if build.status == status:
                    return build.status
                elif time.time() - start > timeout:
                    return build.status
            time.sleep(1)

    def test_zlib(self):
        self.__setup_build(
            url="https://github.com/conan-io/conan-center-index.git",
            path="recipes/zlib/all",
            version="1.2.11",
            sha="317384650cf80725f12243a3ec1adf2c8ca869ef",
        )
        self.agent.start()
        self.assertEqual(self.__wait_for_build_status(database.BuildStatus.success, 300), database.BuildStatus.success)
