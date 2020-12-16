from conanci import database


def create_repo():
    repo = database.Repo()
    repo.url = "https://github.com/uboot/conan-ci.git"
    repo.path = "packages/hello"
    return repo


def create_new_commit():
    commit = database.Commit()
    commit.repo = create_repo()
    commit.channel = create_channel()
    commit.sha = "2777a37dc82e296d55c23f738b79f139e627920c" # first commit
    commit.status = database.CommitStatus.new
    return commit


def create_building_commit():
    commit = database.Commit()
    commit.repo = create_repo()
    commit.channel = create_channel()
    commit.sha = "2777a37dc82e296d55c23f738b79f139e627920c" # first commit
    commit.status = database.CommitStatus.building
    return commit


def create_invalid_repo():
    repo = database.Repo()
    repo.url = "https://github.com/uboot/nonsense.git"
    return repo


def create_channel():
    channel = database.Channel()
    channel.branch = "master"
    channel.name = "stable"
    return channel


def create_linux_profile():
    linux = database.Profile()
    linux.name = "GCC 9"
    linux.container = "uboot/gcc9:latest"
    linux.settings = [
        database.Setting("os", "Linux"),
        database.Setting("build_type", "Release")
    ]
    return linux


def create_windows_profile():
    windows = database.Profile()
    windows.name = "MSVC 15"
    windows.container = "msvc15:local"
    windows.settings = [
        database.Setting("os", "Windows"),
        database.Setting("build_type", "Release")
    ]


def create_build():
    build = database.Build()
    build.commit = create_building_commit()
    build.profile = create_linux_profile()
    build.status = database.BuildStatus.new
    return build

