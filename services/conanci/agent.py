from conanci import database
from conanci.builder import Builder
from conanci.config import connect_to_database, logger
from conanci.worker import Worker
import asyncio
import os
import string


conan_server = os.environ.get("CONAN_SERVER_URL", "127.0.0.1")
conan_user = os.environ.get("CONAN_SERVER_USER", "demo")
conan_password = os.environ.get("CONAN_SERVER_PASSWORD", "demo")
conanci_user = os.environ.get("CONANCI_USER", "conanci")
conanci_os = os.environ.get("CONANCI_AGENT_OS", "Linux")
ssh_dir = os.environ.get("SSH_DIR", "/config-map")
ssh_key = os.environ.get("SSH_KEY", "")


build_template = string.Template(
"""sh -c \" \
conan create $package_path $channel
\"\
"""
)

class Agent(Worker):
    def __init__(self):
        super().__init__()
        connect_to_database()
        self.__build_id = None

    async def work(self):
        new_builds = True
        while new_builds:
            try:
                new_builds = await self.__process_builds()
            except Exception as e:
                logger.error("Processing builds failed: %s", e)

    async def __process_builds(self):
        # database.populate_database()
        # return
        logger.info("Start processing builds")
        with database.session_scope() as session:
            build = session\
                .query(database.Build)\
                .join(database.Build.profile).join(database.Profile.settings)\
                .filter(database.Setting.key=='os',\
                    database.Setting.value==conanci_os,\
                    database.Build.status==database.BuildStatus.new)\
                .populate_existing()\
                .with_for_update(skip_locked=True, of=database.Build)\
                .first()

            if not build:
                logger.info("Stop processing builds with *no* builds processed")
                return False
        
            logger.info("Set status of build '%d' to 'active'", build.id)
            self.__build_id = build.id
            build.status = database.BuildStatus.active

            container = build.profile.container
            parameters = {
                "conan_url": conan_server,
                "conan_user": conan_user,
                "conan_password": conan_password,
                "git_url": build.commit.repo.url,
                "git_sha": build.commit.sha,
                "conanci_user": conanci_user,
                "channel": build.commit.channel.name,
                "path": os.path.join(build.commit.repo.path, "conanfile.py")
                        if build.commit.repo.path != "" else "conanfile.py",
                "ssh_key": build.profile.ecosystem.ssh_key,
                "known_hosts": build.profile.ecosystem.known_hosts
            }

        try:
            with Builder(conanci_os, container) as builder:
                builder_task = asyncio.create_task(self.__run_build(builder, parameters))
                # while running the build check if the build is set to stopping
                while True:
                    done, _ = await asyncio.wait({builder_task}, timeout=10)
                    if done:
                        break

                    with database.session_scope() as session:
                        build = session.query(database.Build) \
                            .filter_by(id=self.__build_id, status=database.BuildStatus.stopping) \
                            .first()
                        if build:
                            logger.info("Cancel build '%d'", self.__build_id)
                            builder.cancel()
                            logger.info("Set status of build '%d' to 'stopped'", self.__build_id)
                            build.status = database.BuildStatus.stopped
                            self.__build_id = None
                            return True

                logger.info("Set status of build '%d' to 'success'", self.__build_id)
                self.__set_build_status(database.BuildStatus.success)
                self.__build_id = None
        except Exception as e:
            logger.error(e)
            logger.info("Set status of build '%d' to 'error'", self.__build_id)
            self.__set_build_status(database.BuildStatus.error)
            self.__build_id = None
            
        return True

    def cleanup(self):
        if not self.__build_id:
            return

        logger.info("Set status of build '%d' to 'new'", self.__build_id)
        self.__set_build_status(database.BuildStatus.new)

    def __set_build_status(self, status):
        if not self.__build_id:
            return

        with database.session_scope() as session:
            build = session.query(database.Build) \
                .filter_by(id=self.__build_id) \
                .first()
            if build:
                build.status = status
                self.__build_id = None
            else:
                logger.error("Failed to find build '%d' in database", self.__build_id)

    async def __run_build(self, builder, parameters):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, builder.pull)
        await loop.run_in_executor(None, builder.setup, parameters)
        await loop.run_in_executor(None, builder.run)