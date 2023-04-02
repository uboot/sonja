from sonja.builder import Builder, BuildFailed

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


known_hosts = ("""
fDF8Q0tlSUMzMndYc2krVHNpNXhKOUV4MUFIOStFPXxtdHBoQVdRa3YydTF6b2IzRFE5d1BuV2dV
QWM9IHNzaC1lZDI1NTE5IEFBQUFDM056YUMxbFpESTFOVEU1QUFBQUlPTXFxbmtWenJtMFNkRzZV
T29xS0xzYWJnSDVDOW9rV2kwZGgybDlHS0psCnwxfGh1K1A4Mys3NE0yYVZhd3VsZENuakdhaXdP
ST18UGx3QkhSbEgvTGFxOXZaei84VTNuamxxZ3c4PSBzc2gtcnNhIEFBQUFCM056YUMxeWMyRUFB
QUFEQVFBQkFBQUJnUUNqN25kTnhRb3dnY1FuanNoY0xycVBFaWlwaG50K1ZUVHZEUDZtSEJMOWox
YU5Va1k0VWUxZ3Z3bkdMVmxPaEdlWXJuWmFNZ1JLNitQS0NVWGFEYkM3cXRiVzhnSWtoTDdhR0Nz
T3IvQzU2U0pNeS9CQ1pmeGQxbld6QU94U0RQZ1ZzbWVyT0JZZk5xbHRWOS9oV0NxQnl3SU5JUis1
ZElnNkpUSjcycGNFcEVqY1lnWGtFMllFRlhWMUpIbnNLZ2JMV05saFNjcWIyVW15UmtReXl0Ukx0
TCszOFRHeGt4Q2ZsbU8rNVo4Q1NTTlk3R2lkak1JWjdRNHpNakEybjFuR3JsVERrendEQ3N3K3dx
RlBHUUExNzljbmZHV09XUlZydWoxNno2WHl2eHZqSndiejB3UVo3NVhLNXRLU2I3Rk55ZUlFczRU
VDRqaytTNGRoUGVBVUM1eStiRFlpcllnTTRHQzd1RW56dG5aeWFWV1E3QjM4MUFLNFFkcnd0NTFa
cUV4S2JRcFRVTm4rRWpxb1R3dnFOajRrcXg1UVVDSTBUaFMvWWtPeEpDWG1QVVdaYmhqcENnNTZp
KzJhQjZDbUsySkdobjU3SzVtajBNTmRCWEE0L1dud0g2WG9QV0p6SzVOeXUyekIzbkFacCtTNWhw
UXMrcDF2TjEvd3Nqaz0KfDF8aFNHUGd0bEI5TFpoWHBxWS9wRnJOaTNndEJNPXx3eXNBREUzWWRk
SWVrY2dkaUNaQ3RodWNCZlE9IGVjZHNhLXNoYTItbmlzdHAyNTYgQUFBQUUyVmpaSE5oTFhOb1lU
SXRibWx6ZEhBeU5UWUFBQUFJYm1semRIQXlOVFlBQUFCQkJFbUtTRU5qUUVlek9teGtaTXk3b3BL
Z3dGQjlua3Q1WVJyWU1qTnVHNU44N3VSZ2c2Q0xyYm81d0FkVC95NnYwbUtWMFUydzBXWjJZQi8r
K1Rwb2NrZz0K
""")


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


def get_build_parameters(profile, https=False, version="", no_user=False):
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
        "conan_profile": profile,
        "conan_options": "-o base:with_tests=False",
        "conan_remote": "default",
        "git_url": "https://uboot@github.com/uboot/private-packages.git" if https else "git@github.com:uboot/sonja-backend.git",
        "git_sha": "fe73ab663d73ee8084cb739240d033987e708d06" if https else "47c5d1dfa67726af1e67530d4f47bf2eb77b0b41",
        "git_credentials": [{
            "url": "https://uboot@github.com",
            "username": "",
            "password": os.environ.get("GIT_PAT", "")
        }],
        "sonja_user": "sonja" if not no_user else "",
        "channel": "latest" if not no_user else "",
        "path": path,
        "version": version,
        "ssh_key": os.environ.get("SSH_KEY", ""),
        "known_hosts": known_hosts,
        "docker_credentials": [{
            "server": "",
            "username": os.environ.get("DOCKER_USER", ""),
            "password": os.environ.get("DOCKER_PASSWORD", "")
        }],
        "conan_credentials": [{
            "remote": "default",
            "username": "agent",
            "password": os.environ.get("CONAN_PASSWORD", "")
        }],
        "mtu": "1450"
    }


class TestBuilder(unittest.TestCase):
    def test_pull_invalid_image_linux(self):
        docker_host = os.environ.get("LINUX_DOCKER_HOST", "")
        parameters = get_build_parameters("linux-debug")
        with environment("DOCKER_HOST", docker_host), Builder("Linux", "uboot/invalid:1.2.3", parameters) as builder:
            self.assertRaises(BuildFailed, builder.pull_image)

    def test_create_build_files_linux(self):
        parameters = get_build_parameters("linux-debug")
        parameters["conan_credentials"].append({
            "remote": "remote",
            "username": "user",
            "password": r'pass" \ word'
        })
        with environment("DOCKER_HOST", ""), Builder("Linux", "uboot/invalid:1.2.3", parameters) as builder:
            builder.create_build_files()
            # with open("build.tar", "wb") as dump:
            #     dump.write(builder.build_files.read())

    def test_create_build_files_windows(self):
        parameters = get_build_parameters("windows-debug")
        parameters["conan_credentials"].append({
            "remote": "remote",
            "username": "user",
            "password": r'pass" \ word'
        })
        with environment("DOCKER_HOST", ""), Builder("Windows", "uboot/invalid:1.2.3", parameters) as builder:
            builder.create_build_files()
            # with open("build.tar", "wb") as dump:
            #     dump.write(builder.build_files.read())

    def test_run_linux(self):
        docker_host = os.environ.get("LINUX_DOCKER_HOST", "")
        parameters = get_build_parameters("linux-debug")
        with environment("DOCKER_HOST", docker_host), Builder("Linux", "uboot/gcc9:latest", parameters) as builder:
            builder.pull_image()
            builder.create_build_files()
            builder.setup_container()
            builder.run_build()
            logs = [line for line in builder.get_log_lines()]
            self.assertGreater(len(logs), 0)
            self.assertTrue("create" in builder.build_output.keys())
            self.assertTrue("info" in builder.build_output.keys())
            self.assertTrue("lock" in builder.build_output.keys())

    def test_run_linux_private_registry(self):
        docker_host = os.environ.get("LINUX_DOCKER_HOST", "")
        parameters = get_build_parameters("linux-debug")
        with environment("DOCKER_HOST", docker_host), Builder("Linux", "uboot/private:latest", parameters) as builder:
            builder.pull_image()
            builder.create_build_files()
            builder.setup_container()
            builder.run_build()
            logs = [line for line in builder.get_log_lines()]
            self.assertGreater(len(logs), 0)
            self.assertTrue("create" in builder.build_output.keys())
            self.assertTrue("info" in builder.build_output.keys())
            self.assertTrue("lock" in builder.build_output.keys())

    def test_run_linux_version(self):
        docker_host = os.environ.get("LINUX_DOCKER_HOST", "")
        parameters = get_build_parameters("linux-debug", version="1.2.3")
        with environment("DOCKER_HOST", docker_host), Builder("Linux", "uboot/gcc9:latest", parameters) as builder:
            builder.pull_image()
            builder.create_build_files()
            builder.setup_container()
            builder.run_build()
            logs = [line for line in builder.get_log_lines()]
            self.assertGreater(len(logs), 0)
            self.assertTrue("create" in builder.build_output.keys())
            self.assertTrue("info" in builder.build_output.keys())
            self.assertTrue("lock" in builder.build_output.keys())

    def test_run_linux_no_user(self):
        docker_host = os.environ.get("LINUX_DOCKER_HOST", "")
        parameters = get_build_parameters("linux-debug", no_user=True)
        with environment("DOCKER_HOST", docker_host), Builder("Linux", "uboot/gcc9:latest", parameters) as builder:
            builder.pull_image()
            builder.create_build_files()
            builder.setup_container()
            builder.run_build()
            logs = [line for line in builder.get_log_lines()]
            self.assertGreater(len(logs), 0)
            self.assertTrue("create" in builder.build_output.keys())
            self.assertTrue("info" in builder.build_output.keys())
            self.assertTrue("lock" in builder.build_output.keys())

    def test_run_linux_version_no_user(self):
        docker_host = os.environ.get("LINUX_DOCKER_HOST", "")
        parameters = get_build_parameters("linux-debug", version="1.2.3", no_user=True)
        with environment("DOCKER_HOST", docker_host), Builder("Linux", "uboot/gcc9:latest", parameters) as builder:
            builder.pull_image()
            builder.create_build_files()
            builder.setup_container()
            builder.run_build()
            logs = [line for line in builder.get_log_lines()]
            self.assertGreater(len(logs), 0)
            self.assertTrue("create" in builder.build_output.keys())
            self.assertTrue("info" in builder.build_output.keys())
            self.assertTrue("lock" in builder.build_output.keys())

    def test_run_linux_wrong_version(self):
        docker_host = os.environ.get("LINUX_DOCKER_HOST", "")
        parameters = get_build_parameters("linux-debug", version="xxx")
        with environment("DOCKER_HOST", docker_host), Builder("Linux", "uboot/gcc9:latest", parameters) as builder:
            builder.pull_image()
            builder.create_build_files()
            builder.setup_container()
            self.assertRaises(BuildFailed, builder.run_build)

    def test_run_linux_https(self):
        docker_host = os.environ.get("LINUX_DOCKER_HOST", "")
        parameters = get_build_parameters("linux-debug", https=True)
        with environment("DOCKER_HOST", docker_host), Builder("Linux", "uboot/gcc9:latest", parameters) as builder:
            builder.pull_image()
            builder.create_build_files()
            builder.setup_container()
            builder.run_build()
            logs = [line for line in builder.get_log_lines()]
            self.assertGreater(len(logs), 0)
            self.assertTrue("create" in builder.build_output.keys())
            self.assertTrue("info" in builder.build_output.keys())
            self.assertTrue("lock" in builder.build_output.keys())

    def test_cancel_linux_immediately(self):
        docker_host = os.environ.get("LINUX_DOCKER_HOST", "")
        parameters = get_build_parameters("linux-debug")
        parameters["path"] = "packages/deadlock/conanfile.py"
        with environment("DOCKER_HOST", docker_host), Builder("Linux", "uboot/gcc9:latest", parameters) as builder:
            canceller = cancel_build(builder, 0)
            builder.pull_image()
            builder.create_build_files()
            builder.setup_container()
            builder.run_build()
            canceller.join()

    def test_cancel_linux(self):
        docker_host = os.environ.get("LINUX_DOCKER_HOST", "")
        parameters = get_build_parameters("linux-debug")
        parameters["path"] = "packages/deadlock/conanfile.py"
        with environment("DOCKER_HOST", docker_host), Builder("Linux", "uboot/gcc9:latest", parameters) as builder:
            canceller = cancel_build(builder, 3)
            builder.pull_image()
            builder.create_build_files()
            builder.setup_container()
            builder.run_build()
            canceller.join()

    def test_run_windows(self):
        docker_host = os.environ.get("WINDOWS_DOCKER_HOST", "127.0.0.1:2375")
        parameters = get_build_parameters("windows-debug")
        with environment("DOCKER_HOST", docker_host), Builder("Windows", "msvc15:local", parameters) as builder:
            builder.pull_image()
            builder.create_build_files()
            builder.setup_container()
            builder.run_build()
            logs = [line for line in builder.get_log_lines()]
            self.assertGreater(len(logs), 0)
            self.assertTrue("create" in builder.build_output.keys())
            self.assertTrue("info" in builder.build_output.keys())
            self.assertTrue("lock" in builder.build_output.keys())

    def test_run_windows_no_user(self):
        docker_host = os.environ.get("WINDOWS_DOCKER_HOST", "127.0.0.1:2375")
        parameters = get_build_parameters("windows-debug", no_user=True)
        with environment("DOCKER_HOST", docker_host), Builder("Windows", "msvc15:local", parameters) as builder:
            builder.pull_image()
            builder.create_build_files()
            builder.setup_container()
            builder.run_build()
            logs = [line for line in builder.get_log_lines()]
            self.assertGreater(len(logs), 0)
            self.assertTrue("create" in builder.build_output.keys())
            self.assertTrue("info" in builder.build_output.keys())
            self.assertTrue("lock" in builder.build_output.keys())

    def test_run_windows_version_no_user(self):
        docker_host = os.environ.get("WINDOWS_DOCKER_HOST", "127.0.0.1:2375")
        parameters = get_build_parameters("windows-debug", version="1.2.3", no_user=True)
        with environment("DOCKER_HOST", docker_host), Builder("Windows", "msvc15:local", parameters) as builder:
            builder.pull_image()
            builder.create_build_files()
            builder.setup_container()
            builder.run_build()
            logs = [line for line in builder.get_log_lines()]
            self.assertGreater(len(logs), 0)
            self.assertTrue("create" in builder.build_output.keys())
            self.assertTrue("info" in builder.build_output.keys())
            self.assertTrue("lock" in builder.build_output.keys())

    def test_run_windows_version(self):
        docker_host = os.environ.get("WINDOWS_DOCKER_HOST", "127.0.0.1:2375")
        parameters = get_build_parameters("windows-debug", version="1.2.3")
        with environment("DOCKER_HOST", docker_host), Builder("Windows", "msvc15:local", parameters) as builder:
            builder.pull_image()
            builder.create_build_files()
            builder.setup_container()
            builder.run_build()
            logs = [line for line in builder.get_log_lines()]
            self.assertGreater(len(logs), 0)
            self.assertTrue("create" in builder.build_output.keys())
            self.assertTrue("info" in builder.build_output.keys())
            self.assertTrue("lock" in builder.build_output.keys())

    def test_run_windows_https(self):
        docker_host = os.environ.get("WINDOWS_DOCKER_HOST", "127.0.0.1:2375")
        parameters = get_build_parameters("windows-debug", https=True)
        with environment("DOCKER_HOST", docker_host), Builder("Windows", "msvc15:local", parameters) as builder:
            builder.pull_image()
            builder.create_build_files()
            builder.setup_container()
            builder.run_build()
            logs = [line for line in builder.get_log_lines()]
            self.assertGreater(len(logs), 0)
            self.assertTrue("create" in builder.build_output.keys())
            self.assertTrue("info" in builder.build_output.keys())
            self.assertTrue("lock" in builder.build_output.keys())

    def test_cancel_windows(self):
        docker_host = os.environ.get("WINDOWS_DOCKER_HOST", "127.0.0.1:2375")
        parameters = get_build_parameters("windows-debug")
        parameters["path"] = "packages/deadlock/conanfile.py"
        with environment("DOCKER_HOST", docker_host), Builder("Windows", "msvc15:local", parameters) as builder:
            canceller = cancel_build(builder, 3)
            builder.pull_image()
            builder.create_build_files()
            builder.setup_container()
            builder.run_build()
            canceller.join()
