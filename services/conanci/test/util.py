from conanci import database


def create_repo(parameters=dict()):
    repo = database.Repo()
    if parameters.get("repo.invalid", False):
        repo.url = "https://github.com/uboot/nonsense.git"
    else:
        repo.url = "https://github.com/uboot/conan-ci.git"
    if parameters.get("repo.deadlock", False):
        repo.path = "packages/deadlock"
    else:
        repo.path = "packages/hello"
    return repo


def create_commit(parameters=dict()):
    commit = database.Commit()
    commit.repo = create_repo(parameters)
    commit.channel = create_channel(parameters)
    commit.sha = "08979da6c039dd919292f7408785e2ad711b2fd5"
    commit.status = parameters.get("commit.status", database.CommitStatus.new)
    return commit


def create_channel(parameters=dict()):
    channel = database.Channel()
    channel.branch = "master"
    channel.name = "stable"
    return channel


def create_profile(parameters=dict()):
    profile = database.Profile()
    if parameters.get("profile.os", "Linux") == "Linux":
        profile.name = "GCC 9"
        profile.container = "uboot/gcc9:latest"
        profile.settings = [
            database.Setting("os", "Linux"),
            database.Setting("build_type", "Release")
        ]
    else:
        profile.name = "MSVC 15"
        profile.container = "msvc15:local"
        profile.settings = [
            database.Setting("os", "Windows"),
            database.Setting("build_type", "Release")
        ]
    return profile


def create_build(parameters=dict()):
    build = database.Build()
    parameters["commit.status"] = database.CommitStatus.building
    build.commit = create_commit(parameters)
    build.profile = create_profile(parameters)
    build.status = database.BuildStatus.new
    return build


