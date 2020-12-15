from conanci.builder import Builder

import os
import unittest
from contextlib import contextmanager


@contextmanager
def environment(key, value):
    os.environ[key] = value
    yield
    del os.environ[key]


class BuilderTest(unittest.TestCase):
    def test_run_linux(self):
        docker_host = os.environ.get("LINUX_DOCKER_HOST", "")
        ssh_key_path = os.environ.get("SSH_KEY_PATH", "")
        parameters =  {
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
        with environment("DOCKER_HOST", docker_host), Builder("Linux", "uboot/gcc9:latest") as builder:
            builder.pull()
            builder.setup(parameters)
            builder.run()

    def test_run_windows(self):
        docker_host = os.environ.get("WINDOWS_DOCKER_HOST", "")
        ssh_key_path = os.environ.get("SSH_KEY_PATH", "")
        parameters =  {
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
        with environment("DOCKER_HOST", docker_host), Builder("Windows", "msvc15:local") as builder:
            builder.pull()
            builder.setup(parameters)
            builder.run()