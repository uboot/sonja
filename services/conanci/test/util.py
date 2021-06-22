from conanci import database

import os


def create_ecosystem(parameters=dict()):
    ecosystem = database.Ecosystem()
    ecosystem.name = "Conan CI"
    ecosystem.user = "conanci"
    ecosystem.known_hosts = ("Z2l0aHViLmNvbSwxNDAuODIuMTIxLjQgc3NoLXJzYSBBQUFBQjNOemFDMXljMkVBQUFBQkl3QUFBUUVBcTJBN"
                             "2hSR21kbm05dFVEYk85SURTd0JLNlRiUWErUFhZUENQeTZyYlRyVHR3N1BIa2NjS3JwcDB5VmhwNUhkRUljS3"
                             "I2cExsVkRCZk9MWDlRVXN5Q09WMHd6ZmpJSk5sR0VZc2RsTEppekhoYm4ybVVqdlNBSFFxWkVUWVA4MWVGekx"
                             "RTm5QSHQ0RVZWVWg3VmZERVNVODRLZXptRDVRbFdwWExtdlUzMS95TWYrU2U4eGhIVHZLU0NaSUZJbVd3b0c2"
                             "bWJVb1dmOW56cElvYVNqQit3ZXFxVVVtcGFhYXNYVmFsNzJKK1VYMkIrMlJQVzNSY1QwZU96UWdxbEpMM1JLc"
                             "lRKdmRzakUzSkVBdkdxM2xHSFNaWHkyOEczc2t1YTJTbVZpL3c0eUNFNmdiT0RxblRXbGc3K3dDNjA0eWRHWE"
                             "E4VkppUzVhcDQzSlhpVUZGQWFRPT0K")
    ecosystem.ssh_key = os.environ.get("SSH_KEY", "")
    ecosystem.public_ssh_key = os.environ.get("PUBLIC_SSH_KEY", "")
    ecosystem.conan_remote = os.environ.get("CONAN_SERVER_URL", "http://127.0.0.1:9300")
    ecosystem.conan_verify_ssl = True
    ecosystem.conan_user = "demo"
    ecosystem.conan_password = "demo"
    parameters["ecosystem"] = ecosystem
    return ecosystem


def create_repo(parameters=dict()):
    repo = database.Repo()
    repo.ecosystem = parameters.get("ecosysstem", create_ecosystem(parameters))
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
    commit.message = "Initial commit\n\nVery long and verbose description"
    commit.status = parameters.get("commit.status", database.CommitStatus.new)
    return commit


def create_channel(parameters=dict()):
    channel = database.Channel()
    channel.ecosystem = parameters.get("ecosystem", create_ecosystem(parameters))
    channel.branch = parameters.get("channel.branch", "master")
    channel.name = "stable"
    return channel


def create_profile(parameters=dict()):
    profile = database.Profile()
    profile.ecosystem = parameters.get("ecosysstem", create_ecosystem(parameters))
    if parameters.get("profile.os", "Linux") == "Linux":
        profile.name = "GCC 9"
        profile.container = "uboot/gcc9:latest"
        profile.settings = [
            database.Setting("os", "Linux"),
            database.Setting("build_type", "Debug"),
            database.Setting("compiler.libcxx", "libstdc++11")
        ]
    else:
        profile.name = "MSVC 15"
        profile.container = "msvc15:local"
        profile.settings = [
            database.Setting("os", "Windows"),
            database.Setting("build_type", "Release")
        ]
    return profile


def create_log(parameters=dict()):
    log = database.Log()
    log.logs = "Start build\nRun Build\nUpload..."
    return log


def create_build(parameters=dict()):
    build = database.Build()
    parameters["commit.status"] = database.CommitStatus.building
    build.commit = create_commit(parameters)
    build.profile = create_profile(parameters)
    build.status = database.BuildStatus.new
    build.log = create_log(parameters)
    return build


def create_recipe(parameters=dict()):
    hello = database.Recipe()
    hello.name = parameters.get("recipe.name", "hello")
    hello.version = "1.2.3"
    hello.user = "conanci"
    hello.channel = "stable"
    hello.revision = "08979da6c039dd919292f7408785e2ad711b2fd5"

    return hello


def create_package(parameters=dict()):
    recipe = create_recipe(parameters)
    package = database.Package()
    package.package_id = "cda61897af86d277c61b93fa40c92da744abdf33"
    package.recipe = recipe

    if parameters.get("package.requirement", False):
        app = database.Package()
        app.requires.append(package)
        app.recipe = create_recipe({"recipe.name": "app"})
        app.package_id = "cda61897af86d277c61b93fa40c92da744abdf33"

    return package
