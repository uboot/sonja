from datetime import datetime
from sonja.model import Ecosystem, Repo, Label, Option, Profile, Platform, Channel, \
    Commit, Build, BuildStatus, LogLine, Run, RunStatus, DockerCredential, ConanCredential, CommitStatus
from sonja.database import logger, Session, session_scope, get_current_configuration
from sonja.redis import RedisClient


def add_build(redis_client: RedisClient):
    logger.info("Add build")
    with session_scope() as session:
        profile = session.query(Profile).first()
        repo = session.query(Repo).first()
        channel = session.query(Channel).first()

        commit = Commit()
        commit.sha = "1234567890abcdef"
        commit.status = CommitStatus.new
        commit.repo = repo
        commit.channel = channel

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

    def initialize_configuration(self):
        configuration = get_current_configuration(self.__session)
        configuration.known_hosts = (
            "Z2l0aHViLmNvbSwxNDAuODIuMTIxLjQgc3NoLXJzYSBBQUFBQjNOemFDMXljMkVBQUFBQkl3QUFBUUVBcTJBN"
            "2hSR21kbm05dFVEYk85SURTd0JLNlRiUWErUFhZUENQeTZyYlRyVHR3N1BIa2NjS3JwcDB5VmhwNUhkRUljS3"
            "I2cExsVkRCZk9MWDlRVXN5Q09WMHd6ZmpJSk5sR0VZc2RsTEppekhoYm4ybVVqdlNBSFFxWkVUWVA4MWVGekx"
            "RTm5QSHQ0RVZWVWg3VmZERVNVODRLZXptRDVRbFdwWExtdlUzMS95TWYrU2U4eGhIVHZLU0NaSUZJbVd3b0c2"
            "bWJVb1dmOW56cElvYVNqQit3ZXFxVVVtcGFhYXNYVmFsNzJKK1VYMkIrMlJQVzNSY1QwZU96UWdxbEpMM1JLc"
            "lRKdmRzakUzSkVBdkdxM2xHSFNaWHkyOEczc2t1YTJTbVZpL3c0eUNFNmdiT0RxblRXbGc3K3dDNjA0eWRHWE"
            "E4VkppUzVhcDQzSlhpVUZGQWFRPT0K"
        )
        docker_credentials = DockerCredential()
        docker_credentials.server = "ubootsregistry.azurecr.io"
        docker_credentials.username = "ubootsregistry"
        docker_credentials.password = ""
        configuration.docker_credentials = [docker_credentials]

    def initialize_ecosystem(self):
        self.__ecosystem.user = "mycompany"
        self.__ecosystem.conan_config_url = "https://github.com/uboot/conan-config.git"
        self.__ecosystem.conan_config_path = "default"
        self.__ecosystem.conan_config_branch = "master"
        conan_credential = ConanCredential()
        conan_credential.remote = "uboot"
        conan_credential.username = "agent"
        conan_credential.password = ""
        self.__ecosystem.conan_credentials = [conan_credential]

    def create(self):
        hello = Repo()
        hello.name = "Hello"
        hello.ecosystem = self.__ecosystem
        hello.url = "https://github.com/uboot/conan-packages.git"
        hello.path = "hello"
        hello.exclude = [
            Label(value="windows")
        ]
        hello.options = [
            Option(key="hello:shared", value="True")
        ]
        self.__session.add(hello)

        base = Repo()
        base.name = "Base"
        base.ecosystem = self.__ecosystem
        base.url = "https://github.com/uboot/conan-packages.git"
        base.path = "base"
        self.__session.add(base)

        core = Repo()
        core.name = "Core"
        core.ecosystem = self.__ecosystem
        core.url = "https://github.com/uboot/conan-packages.git"
        core.path = "core"
        self.__session.add(core)

        tree = Repo()
        tree.name = "Tree"
        tree.ecosystem = self.__ecosystem
        tree.url = "https://github.com/uboot/conan-packages.git"
        tree.path = "tree"
        self.__session.add(base)

        app = Repo()
        app.name = "App"
        app.ecosystem = self.__ecosystem
        app.url = "https://github.com/uboot/conan-packages.git"
        app.path = "app"
        self.__session.add(app)

        linux_release = Profile()
        linux_release.ecosystem = self.__ecosystem
        linux_release.platform = Platform.linux
        linux_release.name = "GCC 9 Release"
        linux_release.container = "uboot/gcc9:latest"
        linux_release.conan_profile = "linux-release"
        self.__session.add(linux_release)

        linux_debug = Profile()
        linux_debug.ecosystem = self.__ecosystem
        linux_debug.platform = Platform.linux
        linux_debug.name = "GCC 9 Debug"
        linux_debug.container = "uboot/gcc9:latest"
        linux_debug.conan_profile = "linux-debug"
        self.__session.add(linux_debug)

        windows_release = Profile()
        windows_release.ecosystem = self.__ecosystem
        windows_release.platform = Platform.windows
        windows_release.name = "MSVC 15 Release"
        windows_release.container = "ubootsregistry.azurecr.io/msvc15:latest"
        windows_release.conan_profile = "windows-release"
        windows_release.labels = [
            Label(value="windows")
        ]
        self.__session.add(windows_release)

        windows_debug = Profile()
        windows_debug.ecosystem = self.__ecosystem
        windows_debug.platform = Platform.windows
        windows_debug.name = "MSVC 15 Debug"
        windows_debug.container = "ubootsregistry.azurecr.io/msvc15:latest"
        windows_debug.conan_profile = "windows-debug"
        windows_debug.labels = [
            Label(value="windows")
        ]
        self.__session.add(windows_debug)

        channel = Channel()
        channel.ecosystem = self.__ecosystem
        channel.name = "Releases"
        channel.ref_pattern = "heads/main"
        channel.conan_channel = "stable"
        channel.conan_remote = "uboot"
        self.__session.add(channel)


def populate_initial_data(ecosystem_id: int):
    logger.info("Initialize configuration and ecosystem with demo data")
    with session_scope() as session:
        data_creator = DemoDataCreator(session, ecosystem_id)
        data_creator.initialize_configuration()
        data_creator.initialize_ecosystem()
        data_creator.create()


def populate_ecosystem():
    logger.info("Add demo data to the first ecosystem")
    with session_scope() as session:
        data_creator = DemoDataCreator(session, 1)
        data_creator.create()
