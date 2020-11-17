from conanci import database
from conanci.config import app, connect_to_database
from conanci.worker import Worker
import asyncio
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
conanci_os = os.environ.get("CONANCI_AGENT_OS", "Linux")

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
        self.client = docker.from_env()
        self.image = image

    def __enter__(self):
        return self

    def pull(self):
        self.client.images.pull(self.image)

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


class Agent(Worker):
    def __init__(self):
        super().__init__()
        connect_to_database()
        self.__build = None

    async def work(self):
        logger.info("Start building")
        loop = asyncio.get_running_loop()
        # database.populate_database()
        # return

        with database.session_scope() as session:
            # build = database.Build.query\
            build = session\
                .query(database.Build)\
                .join(database.Build.profile).join(database.Profile.settings)\
                .filter(database.Setting.key=='os', database.Setting.value==conanci_os)\
                .populate_existing()\
                .with_for_update(skip_locked=True, of=database.Build)\
                .first()

            if not build:
                return
        
            logger.info("Set status of build '%d' to 'active'", build.id)
            self.__build = build.id
            build.status = database.BuildStatus.active
            session.commit()

            container = build.profile.container
            try:
                with Builder(container) as builder:
                    logger.info("Pull docker image '%s'", container)
                    await loop.run_in_executor(None, builder.pull)
                    logger.info("Setup conan")
                    await loop.run_in_executor(None, builder.setup, conan_server, conan_user, conan_password)
            except Exception as e:
                logger.error(e)
            
            logger.info("Set status of build '%d' to 'success'", build.id)
            self.__build = None
            build.status = database.BuildStatus.success
            session.commit()

    def cleanup(self):
        if not self.__build:
            return

        with database.session_scope() as session:
            build = session.query(database.Build)\
                .filter_by(id=self.__build)\
                .first()
            logger.info("Set status of build '%d' to 'new'", build.id)
            build.status = database.BuildStatus.new
