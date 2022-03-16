from sonja.builder import Builder

import base64
import os
import time
import threading
import unittest
from contextlib import contextmanager

# Requires:
#
# 1. Conan server
# docker run --name conan -d --rm -p 9300:9300 -v <path-to>/conan-server:/root/.conan_server conanio/conan_server:1.28.1
#
# conan-server/server.conf
#
# [write_permissions]
# */*@*/*: demo
#
# [users]
# demo: demo


known_hosts = ("Z2l0aHViLmNvbSwxNDAuODIuMTIxLjQgc3NoLXJzYSBBQUFBQjNOemFDMXljMkVBQUFBQkl3QUFBUUVBcTJBN"
               "2hSR21kbm05dFVEYk85SURTd0JLNlRiUWErUFhZUENQeTZyYlRyVHR3N1BIa2NjS3JwcDB5VmhwNUhkRUljS3"
               "I2cExsVkRCZk9MWDlRVXN5Q09WMHd6ZmpJSk5sR0VZc2RsTEppekhoYm4ybVVqdlNBSFFxWkVUWVA4MWVGekx"
               "RTm5QSHQ0RVZWVWg3VmZERVNVODRLZXptRDVRbFdwWExtdlUzMS95TWYrU2U4eGhIVHZLU0NaSUZJbVd3b0c2"
               "bWJVb1dmOW56cElvYVNqQit3ZXFxVVVtcGFhYXNYVmFsNzJKK1VYMkIrMlJQVzNSY1QwZU96UWdxbEpMM1JLc"
               "lRKdmRzakUzSkVBdkdxM2xHSFNaWHkyOEczc2t1YTJTbVZpL3c0eUNFNmdiT0RxblRXbGc3K3dDNjA0eWRHWE"
               "E4VkppUzVhcDQzSlhpVUZGQWFRPT0K")


@contextmanager
def environment(key, value):
    os.environ[key] = value
    yield
    del os.environ[key]


def cancel_build(builder, seconds):
    class Canceller(threading.Thread):
        def __init__(self, builder, seconds):
            super(Canceller, self).__init__()
            self.__builder = builder
            self.__seconds = seconds

        def run(self):
            time.sleep(self.__seconds)
            self.__builder.cancel()

    canceller = Canceller(builder, seconds)
    canceller.start()
    return canceller


def get_build_parameters(profile, https=False, version=""):
    if https:
        path = "./base/conanfile.py"
    elif version:
        path = "./packages/version/conanfile.py"
    else:
        path = "./packages/base/conanfile.py"

    return {
        "conan_config_url": "git@github.com:uboot/conan-config.git",
        "conan_config_path": "default",
        "conan_config_branch": "",
        "conan_remote": "uboot",
        "conan_user": "agent",
        "conan_password": os.environ.get("CONAN_PASSWORD", ""),
        "conan_profile": profile,
        "conan_options": "-o base:with_tests=False",
        "git_url": "https://uboot@github.com/uboot/conan-packages.git" if https else "git@github.com:uboot/sonja.git",
        "git_sha": "ef89f593ea439d8986aca1a52257e44e7b8fea29" if https else "5a0595725a3e50a48b0cd3d286cb96e39c6eb032",
        "git_credentials": [
            {
                "url": "https://uboot@github.com",
                "username": "",
                "password": os.environ.get("GIT_PAT", "")
            }
        ],
        "sonja_user": "sonja",
        "channel": "latest",
        "path": path,
        "version": version,
        "ssh_key": os.environ.get("SSH_KEY", ""),
        "known_hosts": known_hosts,
        "docker_user": "",
        "docker_password": "",
        "mtu": "1450"
    }


class TestBuilder(unittest.TestCase):
    def test_run_linux(self):
        docker_host = os.environ.get("LINUX_DOCKER_HOST", "")
        parameters = get_build_parameters("linux-debug")
        with environment("DOCKER_HOST", docker_host), Builder("Linux", "uboot/gcc9:latest") as builder:
            builder.pull(parameters)
            builder.setup(parameters)
            builder.run()
            logs = [line for line in builder.get_log_lines()]
            self.assertGreater(len(logs), 0)
            self.assertTrue("create" in builder.build_output.keys())
            self.assertTrue("info" in builder.build_output.keys())

    def test_run_linux_version(self):
        docker_host = os.environ.get("LINUX_DOCKER_HOST", "")
        parameters = get_build_parameters("linux-debug", version="1.2.3")
        with environment("DOCKER_HOST", docker_host), Builder("Linux", "uboot/gcc9:latest") as builder:
            builder.pull(parameters)
            builder.setup(parameters)
            builder.run()
            logs = [line for line in builder.get_log_lines()]
            self.assertGreater(len(logs), 0)
            self.assertTrue("create" in builder.build_output.keys())
            self.assertTrue("info" in builder.build_output.keys())

    def test_run_linux_https(self):
        docker_host = os.environ.get("LINUX_DOCKER_HOST", "")
        parameters = get_build_parameters("linux-debug", https=True)
        with environment("DOCKER_HOST", docker_host), Builder("Linux", "uboot/gcc9:latest") as builder:
            builder.pull(parameters)
            builder.setup(parameters)
            builder.run()
            logs = [line for line in builder.get_log_lines()]
            self.assertGreater(len(logs), 0)
            self.assertTrue("create" in builder.build_output.keys())
            self.assertTrue("info" in builder.build_output.keys())

    def test_cancel_linux_immediately(self):
        docker_host = os.environ.get("LINUX_DOCKER_HOST", "")
        parameters = get_build_parameters("linux-debug")
        parameters["path"] = "packages/deadlock/conanfile.py"
        with environment("DOCKER_HOST", docker_host), Builder("Linux", "uboot/gcc9:latest") as builder:
            canceller = cancel_build(builder, 0)
            builder.pull(parameters)
            builder.setup(parameters)
            builder.run()
            canceller.join()

    def test_cancel_linux(self):
        docker_host = os.environ.get("LINUX_DOCKER_HOST", "")
        parameters = get_build_parameters("linux-debug")
        parameters["path"] = "packages/deadlock/conanfile.py"
        with environment("DOCKER_HOST", docker_host), Builder("Linux", "uboot/gcc9:latest") as builder:
            canceller = cancel_build(builder, 3)
            builder.pull(parameters)
            builder.setup(parameters)
            builder.run()
            canceller.join()

    def test_run_windows(self):
        docker_host = os.environ.get("WINDOWS_DOCKER_HOST", "127.0.0.1:2375")
        parameters = get_build_parameters("windows-debug")
        with environment("DOCKER_HOST", docker_host), Builder("Windows", "uboot/msvc15:latest") as builder:
            builder.pull(parameters)
            builder.setup(parameters)
            builder.run()
            logs = [line for line in builder.get_log_lines()]
            self.assertGreater(len(logs), 0)
            self.assertTrue("create" in builder.build_output.keys())
            self.assertTrue("info" in builder.build_output.keys())

    def test_run_windows_version(self):
        docker_host = os.environ.get("WINDOWS_DOCKER_HOST", "127.0.0.1:2375")
        parameters = get_build_parameters("windows-debug", version="1.2.3")
        with environment("DOCKER_HOST", docker_host), Builder("Windows", "uboot/msvc15:latest") as builder:
            builder.pull(parameters)
            builder.setup(parameters)
            builder.run()
            logs = [line for line in builder.get_log_lines()]
            self.assertGreater(len(logs), 0)
            self.assertTrue("create" in builder.build_output.keys())
            self.assertTrue("info" in builder.build_output.keys())

    def test_run_windows_https(self):
        docker_host = os.environ.get("WINDOWS_DOCKER_HOST", "127.0.0.1:2375")
        parameters = get_build_parameters("windows-debug", https=True)
        with environment("DOCKER_HOST", docker_host), Builder("Windows", "uboot/msvc15:latest") as builder:
            builder.pull(parameters)
            builder.setup(parameters)
            builder.run()
            logs = [line for line in builder.get_log_lines()]
            self.assertGreater(len(logs), 0)
            self.assertTrue("create" in builder.build_output.keys())
            self.assertTrue("info" in builder.build_output.keys())

    def test_cancel_windows(self):
        docker_host = os.environ.get("WINDOWS_DOCKER_HOST", "127.0.0.1:2375")
        parameters = get_build_parameters("windows-debug")
        parameters["path"] = "packages/deadlock/conanfile.py"
        with environment("DOCKER_HOST", docker_host), Builder("Windows", "uboot/msvc15:latest") as builder:
            canceller = cancel_build(builder, 3)
            builder.pull(parameters)
            builder.setup(parameters)
            builder.run()
            canceller.join()
