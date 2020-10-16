from conanci.config import app, db
from conanci import database
import docker
import os
import re
from string import Template

data_dir = os.environ.get("VCS_DATA_DIR", "/data")
logger = app.app.logger
docker_image_pattern = "([a-z0-9\\.-]+(:[0-9]+)?)?[a-z0-9\\.-/]+[:@]([a-z0-9\\.-]+)$"
conan_server = os.environ.get("CONAN_SERVER_URL", "127.0.0.1")
conan_user = os.environ.get("CONAN_SERVER_USER", "agent")
conan_password = os.environ.get("CONAN_SERVER_PASSWORD", "demo")
conan_channel = os.environ.get("CONANCI_CHANNEL", "conanci")
script_template = Template(
"""sh -c \" \
git init . \
&& git remote add origin $git_url \
&& git fetch origin $git_sha \
&& git checkout FETCH_HEAD \
&& conan remote clean \
&& conan remote add server $conan_url \
&& conan user -r server -p $conan_password agent
\"
"""
)


class Builder(object):
    def pull(self, image):
        self.image = image
        client = docker.from_env()
        client.images.pull(image)

    def run(self, script):
        client = docker.from_env()
        return client.containers.run(image=self.image, command=script, remove=True)


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
    logger.info("Pull docker image '%s'", container)
    builder.pull(container)
    
    script = script_template.substitute(
        git_url=build.commit.repo.url,
        git_sha=build.commit.sha,
        conan_url=conan_server,
        conan_password=conan_password
    )
    print(builder.run(script))
    