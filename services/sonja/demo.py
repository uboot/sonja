from datetime import datetime
from sonja.model import Ecosystem, Repo, Label, Option, Profile, Platform, Channel, \
    Commit, Build, CommitStatus, BuildStatus, LogLine, Run, RunStatus
from sonja.database import logger, Session, session_scope
from sonja.redis import RedisClient
from sonja.ssh import encode, generate_rsa_key
from typing import Dict


def populate_database():
    logger.info("Populate database")
    with session_scope() as session:
        ecosystem = session.query(Ecosystem).filter_by(id=1).first()
        if not ecosystem:
            raise Exception("Found no ecosystem with ID=1")

        hello = Repo()
        hello.name = "Hello"
        hello.ecosystem = ecosystem
        hello.url = "git@github.com:uboot/sonja-backend.git"
        hello.path = "packages/hello"
        hello.exclude = [
            Label(value="debug")
        ]
        hello.options = [
             Option(key="hello:shared", value="False")
        ]
        session.add(hello)

        base = Repo()
        base.name = "Base"
        base.ecosystem = ecosystem
        base.url = "git@github.com:uboot/sonja-backend.git"
        base.path = "packages/base"
        base.exclude = [
            Label(value="debug")
        ]
        session.add(hello)

        app = Repo()
        app.name = "App"
        app.ecosystem = ecosystem
        app.url = "git@github.com:uboot/sonja-backend.git"
        app.path = "packages/app"
        app.exclude = [
            Label(value="debug")
        ]
        session.add(hello)

        linux_release = Profile()
        linux_release.ecosystem = ecosystem
        linux_release.platform = Platform.linux
        linux_release.name = "GCC 9 Release"
        linux_release.container = "uboot/gcc9:latest"
        linux_release.conan_profile = "linux-release"
        session.add(linux_release)

        linux_debug = Profile()
        linux_debug.ecosystem = ecosystem
        linux_debug.platform = Platform.linux
        linux_debug.name = "GCC 9 Debug"
        linux_debug.container = "uboot/gcc9:latest"
        linux_debug.conan_profile = "linux-debug"
        linux_debug.labels = [
            Label(value="debug")
        ]
        session.add(linux_debug)

        windows_release = Profile()
        windows_release.ecosystem = ecosystem
        windows_release.platform = Platform.windows
        windows_release.name = "MSVC 15 Release"
        windows_release.container = "uboot/msvc15:latest"
        windows_release.conan_profile = "windows-release"
        session.add(windows_release)

        windows_debug = Profile()
        windows_debug.ecosystem = ecosystem
        windows_debug.platform = Platform.windows
        windows_debug.name = "MSVC 15 Debug"
        windows_debug.container = "uboot/msvc15:latest"
        windows_debug.conan_profile = "windows-debug"
        windows_debug.labels = [
            Label(value="debug")
        ]
        session.add(windows_debug)

        channel = Channel()
        channel.ecosystem = ecosystem
        channel.name = "Releases"
        channel.branch = "main"
        channel.conan_channel = "stable"
        session.add(channel)

        commit = Commit()
        commit.status = CommitStatus.new
        commit.sha = "6a8a5d108f13ccbc3435133cc28d035795f14698"
        commit.channel = channel
        commit.repo = base
        commit.message = "Some commit"
        commit.user_name = ""
        commit.user_email = ""

        build = Build()
        build.commit = commit
        build.profile = linux_release
        build.status = BuildStatus.new
        build.created = datetime(year=2000, month=1, day=2, hour=13, minute=30)
        session.add(build)

        run = Run()
        run.build = build
        run.started = datetime(year=2000, month=1, day=2, hour=13, minute=40)
        run.updated = datetime(year=2000, month=1, day=2, hour=13, minute=50)
        run.status = RunStatus.active

        session.commit()


def add_build(redis_client: RedisClient):
    logger.info("Add build")
    with session_scope() as session:
        commit = session.query(Commit).first()
        profile = session.query(Profile).first()

        build = Build()
        build.commit = commit
        build.profile = profile
        build.status = BuildStatus.new
        build.created = datetime.utcnow()

        run = Run()
        run.started = datetime.utcnow()
        run.updated = datetime.utcnow()
        run.status = RunStatus.active
        run.build = build

        session.add(build)
        session.commit()

        redis_client.publish_build_update(build)


def add_run(redis_client: RedisClient):
    logger.info("Add run")
    with session_scope() as session:
        build = session.query(Build).first()

        run = Run()
        run.started = datetime.utcnow()
        run.updated = datetime.utcnow()
        run.status = RunStatus.stalled
        run.build = build
        session.add(run)
        session.commit()

        redis_client.publish_run_update(run)


def add_log_line(redis_client: RedisClient):
    logger.info("Add log line")
    with session_scope() as session:
        run = session.query(Run).first()
        num_log_lines = session.query(LogLine).\
            filter(LogLine.run_id == run.id).\
            count()

        log_line = LogLine()
        log_line.time = datetime.utcnow()
        log_line.number = num_log_lines + 1
        log_line.run = run
        log_line.content = "some logs..."
        session.commit()

        redis_client.publish_log_line_update(log_line)


class DemoDataCreator(object):
    def __init__(self, session: Session, ecosystem_id: int):
        self.__session = session
        ecosystem = session.query(Ecosystem).filter_by(id=ecosystem_id).first()
        if not ecosystem:
            raise Exception(f"Found no ecosystem with ID={ecosystem_id}")
        self.__ecosystem = ecosystem

    def create(self):
        private, public = generate_rsa_key()
        self.__ecosystem.ssh_key = encode(private)
        self.__ecosystem.public_ssh_key = encode(public)
        self.__ecosystem.user = ""
        self.__ecosystem.conan_config_url = "https://github.com/uboot/conan-config.git"
        self.__ecosystem.conan_config_path = "default"
        self.__ecosystem.conan_config_branch = "master"
        self.__ecosystem.conan_remote = "uboot"
        self.__ecosystem.conan_user = "agent"
        self.__ecosystem.conan_password = ""

        linux_release = Profile()
        linux_release.ecosystem = self.__ecosystem
        linux_release.platform = Platform.linux
        linux_release.name = "GCC 9 Release"
        linux_release.container = "uboot/gcc9:latest"
        linux_release.conan_profile = "linux-release"
        linux_release.labels = [Label(value="linux")]
        self.__session.add(linux_release)

        windows_release = Profile()
        windows_release.ecosystem = self.__ecosystem
        windows_release.platform = Platform.windows
        windows_release.name = "MSVC 15 Release"
        windows_release.container = "ubootsregistry.azurecr.io/msvc15:latest"
        windows_release.conan_profile = "windows-release"
        windows_release.labels = [Label(value="windows")]
        self.__session.add(windows_release)

        channel = Channel()
        channel.ecosystem = self.__ecosystem
        channel.name = "Releases"
        channel.branch = "master"
        channel.conan_channel = ""
        self.__session.add(channel)

        # self.__create_repo("glib",
        #                    "https://github.com/conan-io/conan-center-index.git",
        #                    "recipes/glib/all",
        #                    "2.72.1")
        #
        # self.__create_repo("zlib",
        #                    "https://github.com/conan-io/conan-center-index.git",
        #                    "recipes/zlib/all",
        #                    "1.2.12")
        #
        # self.__create_repo("libffi",
        #                    "https://github.com/conan-io/conan-center-index.git",
        #                    "recipes/libffi/all",
        #                    "3.4.2")
        #
        # self.__create_repo("gnu-config",
        #                    "https://github.com/conan-io/conan-center-index.git",
        #                    "recipes/gnu-config/all",
        #                    "cci.20210814")
        #
        # self.__create_repo("pcre",
        #                    "https://github.com/conan-io/conan-center-index.git",
        #                    "recipes/pcre/all",
        #                    "8.45")
        #
        # self.__create_repo("bzip2",
        #                    "https://github.com/conan-io/conan-center-index.git",
        #                    "recipes/bzip2/all",
        #                    "1.0.8")
        #
        # self.__create_repo("meson",
        #                    "https://github.com/conan-io/conan-center-index.git",
        #                    "recipes/meson/all",
        #                    "0.62.1")
        #
        # self.__create_repo("ninja",
        #                    "https://github.com/conan-io/conan-center-index.git",
        #                    "recipes/ninja/1.10.x",
        #                    "1.10.2")
        #
        # self.__create_repo("pkgconf",
        #                    "https://github.com/conan-io/conan-center-index.git",
        #                    "recipes/pkgconf/all",
        #                    "1.7.4")
        #
        # self.__create_repo("automake",
        #                    "https://github.com/conan-io/conan-center-index.git",
        #                    "recipes/automake/all",
        #                    "1.16.4")
        #
        # self.__create_repo("autoconf",
        #                    "https://github.com/conan-io/conan-center-index.git",
        #                    "recipes/autoconf/all",
        #                    "2.71")
        #
        # self.__create_repo("m4",
        #                    "https://github.com/conan-io/conan-center-index.git",
        #                    "recipes/m4/all",
        #                    "1.4.19")
        #
        # self.__create_repo("libgettext",
        #                    "https://github.com/conan-io/conan-center-index.git",
        #                    "recipes/libgettext/all",
        #                    "0.21")
        #
        # self.__create_repo("libiconv",
        #                    "https://github.com/conan-io/conan-center-index.git",
        #                    "recipes/libiconv/all",
        #                    "1.16")
        #
        # self.__create_repo("msys2",
        #                    "https://github.com/conan-io/conan-center-index.git",
        #                    "recipes/msys2/all",
        #                    "cci.latest",
        #                    exclude=["linux"])
        #
        # self.__create_repo("libelf",
        #                    "https://github.com/conan-io/conan-center-index.git",
        #                    "recipes/libelf/all",
        #                    "0.8.13")
        #
        # self.__create_repo("libmount",
        #                    "https://github.com/conan-io/conan-center-index.git",
        #                    "recipes/libmount/all",
        #                    "2.36.2")
        #
        # self.__create_repo("libselinux",
        #                    "https://github.com/conan-io/conan-center-index.git",
        #                    "recipes/libselinux/all",
        #                    "3.3",
        #                    exclude=["windows"])
        #
        # self.__create_repo("pcre2",
        #                    "https://github.com/conan-io/conan-center-index.git",
        #                    "recipes/pcre2/all",
        #                    "10.40")
        #
        # self.__create_repo("flex",
        #                    "https://github.com/conan-io/conan-center-index.git",
        #                    "recipes/flex/all",
        #                    "2.6.4",
        #                    exclude=["windows"])

    def __create_repo(self, name: str, url: str, path: str, version: str, options: Dict = dict(), exclude: list = []):
        repo = Repo()
        repo.name = name
        repo.ecosystem = self.__ecosystem
        repo.url = url
        repo.path = path
        repo.version = version
        repo.options = [Option(key=key, value=options[key]) for key in options]
        repo.exclude = [Label(value=value) for value in exclude]
        self.__session.add(repo)
        return repo


def add_demo_data_to_ecosystem(ecosystem_id: int):
    logger.info("Add demo data to ecosystem")
    with session_scope() as session:
        DemoDataCreator(session, ecosystem_id).create()