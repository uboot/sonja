from conanci import database
from conanci.ssh import hash_password

import os


def create_user(parameters):
    user = database.User()
    user.user_name = parameters.get("user.user_name", "user")
    user.first_name = "Joe"
    user.last_name = "Doe"
    user.password = hash_password("password")
    permission = database.Permission()
    permission.label = database.PermissionLabel.write
    user.permissions.append(permission)
    return user


def create_ecosystem(parameters):
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
    ecosystem.conan_config_url = "git@github.com:uboot/conan-ci.git"
    ecosystem.conan_config_path = "conan-config"
    ecosystem.conan_config_branch = ""
    ecosystem.conan_remote = "uboot"
    ecosystem.conan_user = "user"
    ecosystem.conan_password = os.environ.get("CONAN_PASSWORD", "")
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
    else:
        repo.url = "https://github.com/uboot/conan-ci.git"
    if parameters.get("repo.deadlock", False):
        repo.path = "packages/deadlock"
    else:
        repo.path = "packages/hello"
    repo.exclude = [database.Label("desktop")]
    return repo


def create_repo(parameters):
    repo = database.Repo()
    if "ecosystem" in parameters.keys():
        repo.ecosystem = parameters["ecosystem"]
    else:
        repo.ecosystem = create_ecosystem(parameters)
    if parameters.get("repo.invalid", False):
        repo.url = "https://github.com/uboot/nonsense.git"
    else:
        repo.url = "https://github.com/uboot/conan-ci.git"
    if parameters.get("repo.deadlock", False):
        repo.path = "packages/deadlock"
    else:
        repo.path = "packages/hello"
    repo.exclude = [database.Label("desktop")]
    return repo


def create_commit(parameters):
    commit = database.Commit()
    commit.repo = create_repo(parameters)
    commit.channel = create_channel(parameters)
    commit.sha = "08979da6c039dd919292f7408785e2ad711b2fd5"
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
    channel.name = "stable"
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
    recipe_revision.revision = "2b44d2dde63878dd279ebe5d38c60dfaa97153fb"
    return recipe_revision


def create_package(parameters):
    recipe_revision = create_recipe_revision(parameters)
    package = database.Package()
    package.package_id = "227220812d7ea3aa060187bae41abbc9911dfdfd"
    package.recipe_revision = recipe_revision
    return package
