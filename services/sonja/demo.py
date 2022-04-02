from sonja.database import Ecosystem, Repo, Label, logger, session_scope, Option, Profile, Platform, Channel, Session
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

        session.commit()


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
        self.__session.add(linux_release)

        windows_release = Profile()
        windows_release.ecosystem = self.__ecosystem
        windows_release.platform = Platform.windows
        windows_release.name = "MSVC 15 Release"
        windows_release.container = "uboot/msvc15:latest"
        windows_release.conan_profile = "windows-release"
        self.__session.add(windows_release)

        channel = Channel()
        channel.ecosystem = self.__ecosystem
        channel.name = "Releases"
        channel.branch = "master"
        channel.conan_channel = ""
        self.__session.add(channel)

        self.__create_repo("glib",
                           "https://github.com/conan-io/conan-center-index.git",
                           "recipes/glib/all",
                           "2.70.4",
                           {
                               "glib:with_elf": "False",
                               "glib:with_selinux": "False",
                               "glib:with_mount": "False"
                           })

        self.__create_repo("zlib",
                           "https://github.com/conan-io/conan-center-index.git",
                           "recipes/zlib/all",
                           "1.2.12")

        self.__create_repo("libffi",
                           "https://github.com/conan-io/conan-center-index.git",
                           "recipes/libffi/all",
                           "3.4.2")

        self.__create_repo("gnu-config",
                           "https://github.com/conan-io/conan-center-index.git",
                           "recipes/gnu-config/all",
                           "cci.20201022")

        self.__create_repo("pcre",
                           "https://github.com/conan-io/conan-center-index.git",
                           "recipes/pcre/all",
                           "8.45")

        self.__create_repo("bzip2",
                           "https://github.com/conan-io/conan-center-index.git",
                           "recipes/bzip2/all",
                           "1.0.8")

        self.__create_repo("meson",
                           "https://github.com/conan-io/conan-center-index.git",
                           "recipes/meson/all",
                           "0.60.2")

        self.__create_repo("ninja",
                           "https://github.com/conan-io/conan-center-index.git",
                           "recipes/ninja/1.10.x",
                           "1.10.2")

        self.__create_repo("pkgconf",
                           "https://github.com/conan-io/conan-center-index.git",
                           "recipes/pkgconf/all",
                           "1.7.4")

        self.__create_repo("automake",
                           "https://github.com/conan-io/conan-center-index.git",
                           "recipes/automake/all",
                           "1.16.3")

        self.__create_repo("autoconf",
                           "https://github.com/conan-io/conan-center-index.git",
                           "recipes/autoconf/all",
                           "2.71")

        self.__create_repo("m4",
                           "https://github.com/conan-io/conan-center-index.git",
                           "recipes/m4/all",
                           "1.4.19")

    def __create_repo(self, name: str, url: str, path: str, version: str, options: Dict = dict()):
        repo = Repo()
        repo.name = name
        repo.ecosystem = self.__ecosystem
        repo.url = url
        repo.path = path
        repo.version = version
        repo.options = [Option(key=key, value=options[key]) for key in options]
        self.__session.add(repo)


def add_demo_data_to_ecosystem(ecosystem_id: int):
    logger.info("Add demo data to ecosystem")
    with session_scope() as session:
        DemoDataCreator(session, ecosystem_id).create()