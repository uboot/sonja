from datetime import datetime
from typing import Callable
from sonja.auth import hash_password
from sonja.database import session_scope
from sonja.model import Permission, Ecosystem, PermissionLabel, Base, User, GitCredential, Repo, Option, Label, \
    Commit, CommitStatus, Channel, Profile, Platform, Build, BuildStatus, Recipe, RecipeRevision, Package, Run, \
    RunStatus, LogLine

import os


def run_create_operation(op: Callable[[dict], Base], parameter: dict, ecosystem_id: int = 0) -> int:
    with session_scope() as session:
        if ecosystem_id:
            ecosystem = session.query(Ecosystem).filter(Ecosystem.id == ecosystem_id).first()
            parameter["ecosystem"] = ecosystem
        obj = op(parameter)
        session.add(obj)
        session.commit()
        return obj.id


def create_user(parameters: dict) -> User:
    user = User()
    user.user_name = parameters.get("user.user_name", "user")
    user.first_name = "Joe"
    user.last_name = "Doe"
    user.password = hash_password("password")
    read = Permission(label=PermissionLabel.read)
    user.permissions.append(read)
    if parameters.get("user.permissions", "admin") in ("write", "admin"):
        write = Permission(label=PermissionLabel.write)
        user.permissions.append(write)
    if parameters.get("user.permissions", "admin") == "admin":
        admin = Permission(label=PermissionLabel.admin)
        user.permissions.append(admin)

    return user


def create_ecosystem(parameters):
    ecosystem = Ecosystem()
    ecosystem.name = "My Ecosystem"
    ecosystem.user = "sonja"
    ecosystem.known_hosts = ("Z2l0aHViLmNvbSwxNDAuODIuMTIxLjQgc3NoLXJzYSBBQUFBQjNOemFDMXljMkVBQUFBQkl3QUFBUUVBcTJBN"
                             "2hSR21kbm05dFVEYk85SURTd0JLNlRiUWErUFhZUENQeTZyYlRyVHR3N1BIa2NjS3JwcDB5VmhwNUhkRUljS3"
                             "I2cExsVkRCZk9MWDlRVXN5Q09WMHd6ZmpJSk5sR0VZc2RsTEppekhoYm4ybVVqdlNBSFFxWkVUWVA4MWVGekx"
                             "RTm5QSHQ0RVZWVWg3VmZERVNVODRLZXptRDVRbFdwWExtdlUzMS95TWYrU2U4eGhIVHZLU0NaSUZJbVd3b0c2"
                             "bWJVb1dmOW56cElvYVNqQit3ZXFxVVVtcGFhYXNYVmFsNzJKK1VYMkIrMlJQVzNSY1QwZU96UWdxbEpMM1JLc"
                             "lRKdmRzakUzSkVBdkdxM2xHSFNaWHkyOEczc2t1YTJTbVZpL3c0eUNFNmdiT0RxblRXbGc3K3dDNjA0eWRHWE"
                             "E4VkppUzVhcDQzSlhpVUZGQWFRPT0K")
    ecosystem.ssh_key = os.environ.get("SSH_KEY", "")
    ecosystem.public_ssh_key = os.environ.get("PUBLIC_SSH_KEY", "")
    ecosystem.conan_config_url = "git@github.com:uboot/conan-config.git"
    ecosystem.conan_config_path = "empty" if parameters.get("ecosystem.ecosystem.empty_remote", False) else "default"
    ecosystem.conan_config_branch = ""
    ecosystem.conan_remote = "uboot"
    ecosystem.conan_user = "agent"
    ecosystem.conan_password = os.environ.get("CONAN_PASSWORD", "")
    git_credential = GitCredential(url="https://uboot@github.com", username="",
                                            password=os.environ.get("GIT_PAT", ""))
    ecosystem.git_credentials = [git_credential]
    parameters["ecosystem"] = ecosystem
    return ecosystem


def create_repo(parameters):
    repo = Repo()
    repo.name = "Repo Name"
    if "ecosystem" in parameters.keys():
        repo.ecosystem = parameters["ecosystem"]
    else:
        repo.ecosystem = create_ecosystem(parameters)

    if parameters.get("repo.url", ""):
        repo.url = parameters.get("repo.url", "")
    elif parameters.get("repo.invalid", False):
        repo.url = "https://github.com/uboot/nonsense.git"
    elif parameters.get("repo.https", False):
        repo.url = "https://uboot@github.com/uboot/conan-packages.git"
        repo.path = "base"
    else:
        repo.url = "https://github.com/uboot/sonja-backend.git"
        if parameters.get("repo.deadlock", False):
            repo.path = "packages/deadlock"
        elif parameters.get("repo.dependent", False):
            repo.path = "packages/hello"
        else:
            repo.path = "packages/base"
            repo.options = [Option(key="base:with_tests", value="False")]
    repo.exclude = [Label(value="desktop")]
    return repo


def create_commit(parameters):
    commit = Commit()
    commit.repo = create_repo(parameters)
    commit.channel = create_channel(parameters)

    if parameters.get("repo.https", False):
        commit.sha = "ef89f593ea439d8986aca1a52257e44e7b8fea29"
    else:
        commit.sha = "c25c786b0f4e4b8fcaa247feb4809b68e671522d"

    commit.message = "Initial commit\n\nVery long and verbose description"
    commit.user_name = "Joe Smith"
    commit.user_email = "joe.smith@acme.com"
    commit.status = parameters.get("commit.status", CommitStatus.new)
    return commit


def create_channel(parameters):
    channel = Channel()
    if "ecosystem" in parameters.keys():
        channel.ecosystem = parameters["ecosystem"]
    else:
        channel.ecosystem = create_ecosystem(parameters)
    channel.ref_pattern = parameters.get("channel.ref_pattern", "heads/main")
    channel.name = "Releases"
    channel.conan_channel = "stable"
    return channel


def create_profile(parameters):
    profile = Profile()
    if "ecosystem" in parameters.keys():
        profile.ecosystem = parameters["ecosystem"]
    else:
        profile.ecosystem = create_ecosystem(parameters)
    if parameters.get("profile.os", "Linux") == "Linux":
        profile.name = "GCC 9"
        profile.platform = Platform.linux
        profile.container = "uboot/gcc9:latest"
        profile.conan_profile = "linux-debug"
        profile.labels = [Label(value="embedded")]
        profile.platform = Platform.linux
    else:
        profile.name = "MSVC 15"
        profile.platform = Platform.windows
        profile.container = "msvc15:local"
        profile.conan_profile = "windows-release"
        profile.labels = [Label(value="desktop")]
        profile.platform = Platform.windows
    return profile


def create_log_line(parameters):
    log_line = LogLine()
    log_line.number = 1
    log_line.time = datetime(year=2000, month=1, day=2, hour=13, minute=50)
    log_line.content = "Start build..."
    return log_line


def create_build(parameters):
    build = Build()
    parameters["commit.status"] = CommitStatus.building
    build.created = datetime(year=2000, month=1, day=2, hour=13, minute=30)
    build.commit = create_commit(parameters)
    build.profile = create_profile(parameters)
    build.status = parameters.get("build.status", BuildStatus.new)
    if parameters.get("build.with_dependencies", False):
        build.package = create_package(parameters)
    if parameters.get("build.with_missing", False):
        build.missing_recipes = [create_recipe(parameters)]
        build.missing_packages = [create_package(parameters)]
    return build


def create_run(parameters):
    run = Run()
    run.build = create_build(parameters)
    run.started = datetime(year=2000, month=1, day=2, hour=13, minute=40)
    run.updated = parameters.get("run.updated", datetime(year=2000, month=1, day=2, hour=13, minute=45))
    run.status = parameters.get("run.status", RunStatus.active)
    return run


def create_recipe(parameters):
    recipe = Recipe()
    if "ecosystem" in parameters.keys():
        recipe.ecosystem = parameters["ecosystem"]
    else:
        recipe.ecosystem = create_ecosystem(parameters)
    recipe.name = parameters.get("recipe.name", "app")
    recipe.version = "1.2.3"
    recipe.user = None
    recipe.channel = None
    return recipe


def create_recipe_revision(parameters):
    recipe = create_recipe(parameters)
    recipe_revision = RecipeRevision()
    recipe_revision.recipe = recipe
    recipe.current_revision = recipe_revision
    recipe_revision.revision = parameters.get("recipe_revision.revision", "2b44d2dde63878dd279ebe5d38c60dfaa97153fb")
    return recipe_revision


def create_package(parameters):
    recipe_revision = create_recipe_revision(parameters)
    package = Package()
    package.package_id = parameters.get("package.package_id", "227220812d7ea3aa060187bae41abbc9911dfdfd")
    package.recipe_revision = recipe_revision
    return package
