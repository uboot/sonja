from conanci.builder import Builder

import os
import time
import threading
import unittest
from contextlib import contextmanager


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


def get_linux_build_parameters():
    ssh_key_path = os.environ.get("SSH_KEY_PATH", "")
    return {
        "conan_url": os.environ.get("CONAN_SERVER_URL", "127.0.0.1"),
        "conan_user": "demo",
        "conan_password": "demo",
        "git_url": "git@github.com:uboot/conan-ci.git",
        "git_sha": "08979da6c039dd919292f7408785e2ad711b2fd5",
        "conanci_user": "conanci",
        "channel": "latest",
        "path": "packages/hello/conanfile.py",
        "ssh_dir": os.path.dirname(ssh_key_path),
        "ssh_key": os.path.basename(ssh_key_path)
    }


def get_windows_build_parameters():
    ssh_key_path = os.environ.get("SSH_KEY_PATH", "")
    return {
        "conan_url": os.environ.get("CONAN_SERVER_URL", "127.0.0.1"),
        "conan_user": "demo",
        "conan_password": "demo",
        "git_url": "git@github.com:uboot/conan-ci.git",
        "git_sha": "ca8ac0c42b0487a160ef3ac8200de0053b27716c",
        "conanci_user": "conanci",
        "channel": "latest",
        "path": "packages/hello/conanfile.py",
        "ssh_dir": os.path.dirname(ssh_key_path),
        "ssh_key": os.path.basename(ssh_key_path)
    }


class BuilderTest(unittest.TestCase):
    def test_run_linux(self):
        docker_host = os.environ.get("LINUX_DOCKER_HOST", "")
        parameters = get_linux_build_parameters()
        with environment("DOCKER_HOST", docker_host), Builder("Linux", "uboot/gcc9:latest") as builder:
            builder.pull()
            builder.setup(parameters)
            builder.run()

    def test_cancel_linux_immediately(self):
        docker_host = os.environ.get("LINUX_DOCKER_HOST", "")
        parameters = get_linux_build_parameters()
        parameters["path"] = "packages/deadlock/conanfile.py"
        with environment("DOCKER_HOST", docker_host), Builder("Linux", "uboot/gcc9:latest") as builder:
            canceller = cancel_build(builder, 0)
            builder.pull()
            builder.setup(parameters)
            builder.run()
            canceller.join()

    def test_cancel_linux(self):
        docker_host = os.environ.get("LINUX_DOCKER_HOST", "")
        parameters = get_linux_build_parameters()
        parameters["path"] = "packages/deadlock/conanfile.py"
        with environment("DOCKER_HOST", docker_host), Builder("Linux", "uboot/gcc9:latest") as builder:
            canceller = cancel_build(builder, 3)
            builder.pull()
            builder.setup(parameters)
            builder.run()
            canceller.join()

    def test_run_windows(self):
        docker_host = os.environ.get("WINDOWS_DOCKER_HOST", "")
        parameters = get_windows_build_parameters()
        with environment("DOCKER_HOST", docker_host), Builder("Windows", "msvc15:local") as builder:
            builder.pull()
            builder.setup(parameters)
            builder.run()

    def test_cancel_windows(self):
        docker_host = os.environ.get("WINDOWS_DOCKER_HOST", "")
        parameters = get_windows_build_parameters()
        parameters["path"] = "packages/deadlock/conanfile.py"
        with environment("DOCKER_HOST", docker_host), Builder("Windows", "msvc15:local") as builder:
            canceller = cancel_build(builder, 3)
            builder.pull()
            builder.setup(parameters)
            builder.run()
            canceller.join()
