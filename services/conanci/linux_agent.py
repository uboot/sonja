from conanci.config import app, db
from conanci import database
import docker
import os
import re

data_dir = os.environ.get("VCS_DATA_DIR", "/data")
logger = app.app.logger
docker_image_pattern = '([a-z0-9\.-]+(:[0-9]+)?)?[a-z0-9\.-/]+[:@]([a-z0-9\.-]+)$'


class Builder(object):
    def create(self, image):
        client = docker.from_env()
        client.images.pull(image)
        self.container = client.containers.create(image)

    def download(self, url, commit):
        result = self.container.exec_run("git --version")


def process_builds():
    # setup_database()
    # return

    #build = database.Build.query.filter_by(status=database.BuildStatus.new)\
    build = database.Build.query\
            .populate_existing()\
            .with_for_update(skip_locked=True, of=database.Build)\
            .first()
    
    if not build:
        return

    logger.info("Set status of build '%d' to 'active'", build.id)
    build.status = database.BuildStatus.active
    db.session.commit()
    
    container = build.profile.container
    if not re.match(docker_image_pattern, build.profile.container):
        logger.error("The image '%s' is not a valid docker image name",
                     container)
        return

    builder = Builder()
    logger.info("Create a docker container for the image '%s'", container)
    builder.create(container)
