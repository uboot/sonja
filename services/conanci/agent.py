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
        self.__build = None

    async def work(self):
        new_builds = True
        while new_builds:
            new_builds = await self.__process_builds()

    async def __process_builds(self):
        logger.info("Start processing builds")
        loop = asyncio.get_running_loop()
        # database.populate_database()
        # return

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
            self.__build = build.id
            build.status = database.BuildStatus.active
            session.commit()

            container = build.profile.container
            parameters = {
                "conan_url": conan_server,
                "conan_user": conan_user,
                "conan_password": conan_password,
                "git_url": build.commit.repo.url,
                "git_sha": build.commit.sha,
                "conanci_user": conanci_user,
                "channel": build.commit.channel.name,
                "path": build.commit.repo.path if build.commit.repo.path != "" else "."
            }
            try:
                with Builder(conanci_os, container) as builder:
                    await loop.run_in_executor(None, builder.pull)
                    await loop.run_in_executor(None, builder.setup, parameters)
                    await loop.run_in_executor(None, builder.run)

                    logger.info("Set status of build '%d' to 'success'", build.id)
                    build.status = database.BuildStatus.success
                    session.commit()
                    self.__build = None
            except Exception as e:
                logger.error(e)
                logger.info("Set status of build '%d' to 'error'", build.id)
                build.status = database.BuildStatus.error
                session.commit()
                self.__build = None

            logger.info("Finish processing build '%d'", build.id)
            
        return True

    def cleanup(self):
        if not self.__build:
            return

        with database.session_scope() as session:
            build = session.query(database.Build)\
                .filter_by(id=self.__build)\
                .first()
            logger.info("Set status of build '%d' to 'new'", build.id)
            build.status = database.BuildStatus.new
