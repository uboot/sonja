from sonja import database
from sonja.auth import hash_password
from typing import Callable

import os


def run_create_operation(op: Callable[[dict], database.Base], parameter: dict) -> int:
    with database.session_scope() as session:
        obj = op(parameter)
        session.add(obj)
        session.commit()
        return obj.id


def create_user(parameters: dict) -> database.User:
    user = database.User()
    user.user_name = parameters.get("user.user_name", "user")
    user.first_name = "Joe"
    user.last_name = "Doe"
    user.password = hash_password("password")
    read = database.Permission(database.PermissionLabel.read)
    user.permissions.append(read)
    if parameters.get("user.permissions", "admin") in ("write", "admin"):
        write = database.Permission(database.PermissionLabel.write)
        user.permissions.append(write)
    if parameters.get("user.permissions", "admin") == "admin":
        admin = database.Permission(database.PermissionLabel.admin)
        user.permissions.append(admin)

    return user


def create_ecosystem(parameters):
    ecosystem = database.Ecosystem()
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
    ecosystem.conan_config_path = "empty" if parameters.get("ecosystem.ecosystem.empty_remote", "False") else "default"
    ecosystem.conan_config_branch = ""
    ecosystem.conan_remote = "uboot"
    ecosystem.conan_user = "agent"
    ecosystem.conan_password = os.environ.get("CONAN_PASSWORD", "")
    git_credential = database.GitCredential()
    git_credential.url = "https://uboot@github.com"
    git_credential.username = ""
    git_credential.password = os.environ.get("GIT_PAT", "")
    ecosystem.credentials = [git_credential]
    parameters["ecosystem"] = ecosystem
    return ecosystem


def create_repo(parameters):
    repo = database.Repo()
    if "ecosystem" in parameters.keys():
        repo.ecosystem = parameters["ecosystem"]
    else:
        repo.ecosystem = create_ecosystem(parameters)
    if parameters.get("repo.invalid", False):
        repo.url = "https://github.com/uboot/nonsense.git"
    elif parameters.get("repo.https", False):
        repo.url = "https://uboot@github.com/uboot/conan-packages.git"
        repo.path = "base"
    else:
        repo.url = "https://github.com/uboot/sonja.git"
        if parameters.get("repo.deadlock", False):
            repo.path = "packages/deadlock"
        elif parameters.get("repo.dependent", False):
            repo.path = "packages/hello"
        else:
            repo.path = "packages/base"
            repo.options = [database.Option("base:with_tests", "False")]
    repo.exclude = [database.Label("desktop")]
    return repo


def create_commit(parameters):
    commit = database.Commit()
    commit.repo = create_repo(parameters)
    commit.channel = create_channel(parameters)

    if parameters.get("repo.https", False):
        commit.sha = "ef89f593ea439d8986aca1a52257e44e7b8fea29"
    else:
        commit.sha = "c25c786b0f4e4b8fcaa247feb4809b68e671522d"

    commit.message = "Initial commit\n\nVery long and verbose description"
    commit.status = parameters.get("commit.status", database.CommitStatus.new)
    return commit


def create_channel(parameters):
    channel = database.Channel()
    if "ecosystem" in parameters.keys():
        channel.ecosystem = parameters["ecosystem"]
    else:
        channel.ecosystem = create_ecosystem(parameters)
    channel.branch = parameters.get("channel.branch", "master")
    channel.name = "Releases"
    channel.conan_channel = "stable"
    return channel


def create_profile(parameters):
    profile = database.Profile()
    if "ecosystem" in parameters.keys():
        profile.ecosystem = parameters["ecosystem"]
    else:
        profile.ecosystem = create_ecosystem(parameters)
    if parameters.get("profile.os", "Linux") == "Linux":
        profile.name = "GCC 9"
        profile.platform = database.Platform.linux
        profile.container = "uboot/gcc9:latest"
        profile.conan_profile = "linux-debug"
        profile.labels = [database.Label("embedded")]
        profile.platform = database.Platform.linux
    else:
        profile.name = "MSVC 15"
        profile.platform = database.Platform.windows
        profile.container = "msvc15:local"
        profile.conan_profile = "windows-release"
        profile.labels = [database.Label("desktop")]
        profile.platform = database.Platform.windows
    return profile


def create_log(parameters):
    log = database.Log()
    log.logs = "Start build\nRun Build\nUpload..."
    return log


def create_build(parameters):
    build = database.Build()
    parameters["commit.status"] = database.CommitStatus.building
    build.commit = create_commit(parameters)
    build.profile = create_profile(parameters)
    build.status = database.BuildStatus.new
    build.log = create_log(parameters)
    if parameters.get("build.with_dependencies", False):
        build.package = create_package(parameters)
    if parameters.get("build.with_missing", False):
        build.missing_recipes = [create_recipe(parameters)]
        build.missing_packages = [create_package(parameters)]
    return build


def create_recipe(parameters):
    recipe = database.Recipe()
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
    recipe_revision = database.RecipeRevision()
    recipe_revision.recipe = recipe
    recipe_revision.revision = parameters.get("recipe_revision.revision", "2b44d2dde63878dd279ebe5d38c60dfaa97153fb")
    return recipe_revision


def create_package(parameters):
    recipe_revision = create_recipe_revision(parameters)
    package = database.Package()
    package.package_id = parameters.get("package.package_id", "227220812d7ea3aa060187bae41abbc9911dfdfd")
    package.recipe_revision = recipe_revision
    return package
