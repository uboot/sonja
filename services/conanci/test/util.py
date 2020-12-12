from conanci import database


def create_repo():
    repo = database.Repo()
    repo.url = "https://github.com/uboot/conan-ci.git"
    repo.path = "packages/hello"
    return repo


def create_channel():
    channel = database.Channel()
    channel.branch = "master"
    channel.name = "stable"
    return channel


def create_build():
    repo = create_repo()
    channel = create_channel()

    linux = database.Profile()
    linux.name = "GCC 9"
    linux.container = "uboot/gcc9:latest"
    linux.settings = [
        database.Setting("os", "Linux"),
        database.Setting("build_type", "Release")
    ]

    windows = database.Profile()
    windows.name = "MSVC 15"
    windows.container = "msvc15:local"
    windows.settings = [
        database.Setting("os", "Windows"),
        database.Setting("build_type", "Release")
    ]

    commit = database.Commit()
    commit.repo = repo
    commit.sha = "2777a37dc82e296d55c23f738b79f139e627920c"
    commit.channel = channel
    commit.status = database.CommitStatus.new
    build = database.Build()
    build.commit = commit
    build.profile = linux
    build.status = database.BuildStatus.new
    return build

