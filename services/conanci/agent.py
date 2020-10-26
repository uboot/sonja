from conanci.config import app, db
from conanci import database
import docker
import os
import re
import string

logger = app.app.logger
docker_image_pattern = ("([a-z0-9\\.-]+(:[0-9]+)?)?"
                        "[a-z0-9\\.-/]+[:@]([a-z0-9\\.-]+)$")
conan_server = os.environ.get("CONAN_SERVER_URL", "127.0.0.1")
conan_user = os.environ.get("CONAN_SERVER_USER", "agent")
conan_password = os.environ.get("CONAN_SERVER_PASSWORD", "demo")
conanci_user = os.environ.get("CONANCI_USER", "conanci")

setup_template = string.Template(
"""sh -c \" \
conan remote clean \
&& conan remote add server $conan_url \
&& conan user -r server -p $conan_password $conan_user \
\"
"""
)

source_template = string.Template(
"""sh -c \" \
mkdir conanci \
&& cd conanci \
&& git init \
&& git remote add origin $git_url \
&& git fetch origin $git_sha \
&& git checkout FETCH_HEAD \
\"
"""
)

build_template = string.Template(
"""sh -c \" \
conan create $package_path $channel
\"
"""
)


class Builder(object):
    def __init__(self, image):
        if not re.match(docker_image_pattern, image):
            raise Exception("The image '{0}' is not a valid "
                            "docker image name".format(image))

        self.image = image
        self.client = docker.from_env()
        client = docker.from_env()
        client.images.pull(image)

    def __enter__(self):
        return self

    def setup(self, url, user, password):
        setup_script = setup_template.substitute(conan_url=url,
                                                 conan_user=user,
                                                 conan_password=password)
        setup = self.client.containers.create(image=self.image,
                                              command=setup_script)
        try:
            setup.start()
            setup.wait()
            setup.commit(repository="setup", tag="local")
        finally:
            setup.remove()

    def __exit__(self, type, value, traceback):
        try:
            logger.info("Remove all temporary docker images")
            self.client.images.remove("setup:local")
        except docker.errors.ImageNotFound:
            pass


def process_builds():
    # database.populate_database()
    # return

    # build = database.Build.query\
    build = database.Build.query.filter_by(status=database.BuildStatus.new)\
            .populate_existing()\
            .with_for_update(skip_locked=True, of=database.Build)\
            .first()

    if not build:
        return

    logger.info("Set status of build '%d' to 'active'", build.id)
    build.status = database.BuildStatus.active
    db.session.commit()

    container = build.profile.container

    logger.info("Pull docker image '%s'", container)
    try:
        with Builder(container) as builder:
            logger.info("Setup conan")
            builder.setup(url=conan_server, user=conan_user,
                          password=conan_password)
    except Exception as e:
        logger.error(e)
