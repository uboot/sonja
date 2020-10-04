from swagger_server.config import app, db
from swagger_server import database

import sqlalchemy.exc
from conans.client.conan_api import ConanAPIV1

import os

data_dir = os.environ.get("VCS_DATA_DIR", "/data")
logger = app.app.logger

class Conan(object):
    def __init__(self):
        self.api = ConanAPIV1()

    def remotes(self):
        return self.api.remote_list()

def setup_database():
    repo = database.Repo()
    repo.url = "https://github.com/uboot/conan-ci.git"
    repo.path = "packages/hello"
    profile = database.Profile()
    profile.name = "GCC 9"
    profile.container = "conanio/gcc9"
    profile.settings = [database.Setting("build_type", "Release")]
    channel = database.Channel()
    channel.branch = "master"
    channel.name = "stable"
    commit = database.Commit()
    commit.repo = repo
    commit.sha = "2777a37dc82e296d55c23f738b79f139e627920c"
    commit.channel = channel
    commit.status = database.CommitStatus.new
    build = database.Build()
    build.commit = commit
    build.profile = profile
    build.status = database.BuildStatus.new
    db.session.add(build)
    db.session.commit()

def process_builds():
    # setup_database()
    # return

    build = database.Build.query.filter_by(status=database.BuildStatus.new)\
            .populate_existing()\
            .with_for_update(skip_locked=True, of=database.Build)\
            .first()
    
    if not build:
        return

    logger.info("set status of build '%d' to 'active'", build.id)
    build.status = database.BuildStatus.active
    db.session.commit()
    