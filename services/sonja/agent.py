from datetime import datetime
from typing import List

from sonja.builder import Builder, BuildFailed
from sonja.config import connect_to_database, logger
from sonja.database import session_scope
from sonja.redis import RedisClient
from sonja.client import Scheduler
from sonja.manager import Manager
from sonja.model import BuildStatus, Build, Log, Profile, Platform, Run, LogLine
from sonja.worker import Worker
from sqlalchemy import func, update
from sqlalchemy.exc import OperationalError
import asyncio
import os
import time


sonja_os = os.environ.get("SONJA_AGENT_OS", "Linux")
TIMEOUT = 10


async def _run_build(builder, parameters):
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, builder.pull, parameters)
    await loop.run_in_executor(None, builder.setup, parameters)
    await loop.run_in_executor(None, builder.run)


class Agent(Worker):
    def __init__(self, scheduler: Scheduler, redis_client: RedisClient):
        super().__init__()
        connect_to_database()
        self.__build_id = None
        self.__run_id = None
        self.__log_line_counter = None
        self.__scheduler = scheduler
        self.__redis_client = redis_client
        self.__manager = Manager(redis_client)

    async def work(self):
        new_builds = True
        while new_builds:
            try:
                new_builds = await self.__process_builds()
            except Exception as e:
                logger.error("Processing builds failed: %s", e)
                logger.info("Retry in %i seconds", TIMEOUT)
                time.sleep(TIMEOUT)

    async def __process_builds(self):
        logger.info("Start processing builds")
        platform = Platform.linux if sonja_os == "Linux" else Platform.windows
        try:
            with session_scope() as session:
                build = session\
                    .query(Build)\
                    .join(Build.profile)\
                    .filter(Profile.platform == platform,\
                            Build.status == BuildStatus.new)\
                    .populate_existing()\
                    .with_for_update(skip_locked=True, of=Build)\
                    .first()

                if not build:
                    logger.info("Stop processing builds with *no* builds processed")
                    return False

                logger.info("Set status of build '%d' to 'active'", build.id)
                self.__build_id = build.id
                build.status = BuildStatus.active
                run = Run()
                run.build = build
                run.status = BuildStatus.active
                run.started = datetime.utcnow()
                session.commit()
                self.__run_id = run.id
                self.__log_line_counter = 1
                self.__redis_client.publish_build_update(build)

                container = build.profile.container
                parameters = {
                    "conan_config_url": build.profile.ecosystem.conan_config_url,
                    "conan_config_path": build.profile.ecosystem.conan_config_path,
                    "conan_config_branch": build.profile.ecosystem.conan_config_branch,
                    "conan_remote": build.profile.ecosystem.conan_remote,
                    "conan_user": build.profile.ecosystem.conan_user,
                    "conan_password": build.profile.ecosystem.conan_password,
                    "conan_profile": build.profile.conan_profile,
                    "conan_options": " ".join(["-o {0}={1}".format(option.key, option.value)
                                               for option in build.commit.repo.options]),
                    "git_url": build.commit.repo.url,
                    "git_sha": build.commit.sha,
                    "git_credentials": [
                        {
                            "url": c.url,
                            "username": c.username,
                            "password": c.password
                        } for c in build.profile.ecosystem.credentials
                    ],
                    "sonja_user": build.profile.ecosystem.user,
                    "channel": build.commit.channel.conan_channel,
                    "version": "" if not build.commit.repo.version else build.commit.repo.version,
                    "path": "./{0}/{1}".format(build.commit.repo.path, "conanfile.py")
                            if build.commit.repo.path != "" else "./conanfile.py",
                    "ssh_key": build.profile.ecosystem.ssh_key,
                    "known_hosts": build.profile.ecosystem.known_hosts,
                    "docker_user": build.profile.docker_user,
                    "docker_password": build.profile.docker_password,
                    "mtu": os.environ.get("SONJA_MTU", "1500")
                }
        except OperationalError as e:
            logger.error("Failed to access database: %s", e)
            logger.info("Try to reconnect in %i seconds", TIMEOUT)
            time.sleep(TIMEOUT)
            return True

        try:
            with Builder(sonja_os, container) as builder:
                builder_task = asyncio.create_task(_run_build(builder, parameters))
                while True:
                    # wait 10 seconds
                    done, _ = await asyncio.wait({builder_task}, timeout=10)
                    log_lines = [line for line in builder.get_log_lines()]
                    self.__append_to_logs(log_lines)

                    # if finished exit
                    if done:
                        builder_task.result()
                        break

                    # check if the build was stopped and cancel it
                    # if necessary
                    if self.__cancel_stopping_build(builder):
                        return True

                logger.info("Process build output")
                result = self.__manager.process_success(self.__build_id, builder.build_output)
                if result.get("new_builds", False):
                    self.__trigger_scheduler()

                self.__set_build_status(BuildStatus.success)
        except BuildFailed as e:
            logger.info("Build '%d' failed", self.__build_id)
            logger.info("%s", e)
            self.__append_to_logs([str(e)])
            self.__manager.process_failure(self.__build_id, builder.build_output)
            self.__set_build_status(BuildStatus.error)
        except asyncio.CancelledError:
            logger.info("Agent was cancelled")
            self.__set_build_status(BuildStatus.new, BuildStatus.stopped)
            raise
        except Exception as e:
            logger.error("Unexpected error while building: ", e)
            logger.info(e)
        finally:
            self.__build_id = None
            self.__run_id = None
            self.__log_line_counter = None
            
        return True

    def __set_build_status(self, status: BuildStatus, run_status: BuildStatus = None):
        logger.info("Set status of build '%d' to '%s'", self.__build_id, status)

        if not self.__build_id:
            return

        if run_status is None:
            run_status = status

        try:
            with session_scope() as session:
                run = session.query(Run) \
                    .filter_by(id=self.__run_id) \
                    .first()
                if run and run.build:
                    run.status = run_status
                    run.build.status = status
                    session.commit()
                    self.__redis_client.publish_build_update(run.build)
                else:
                    logger.error("Failed to find run '%d' and/or its build in database", self.__run_id)
        except OperationalError as e:
            logger.error("Failed to set build status: %s", e)

    def __append_to_logs(self, log_lines: List[str]):
        try:
            with session_scope() as session:
                for line in log_lines:
                    log_line = LogLine()
                    log_line.content = line.encode("cp1252", errors="replace")
                    log_line.time = datetime.utcnow()
                    log_line.run_id = self.__run_id
                    log_line.number = self.__log_line_counter
                    self.__log_line_counter += 1
                    session.add(log_line)
                    session.commit()
                    self.__redis_client.publish_log_line_update(log_line)
        except OperationalError as e:
            logger.error("Failed to update logs: %s", e)

    def __cancel_stopping_build(self, builder) -> bool:
        try:
            with session_scope() as session:
                build = session.query(Build) \
                    .filter_by(id=self.__build_id, status=BuildStatus.stopping) \
                    .first()
                if not build:
                    return False

                run = session.query(Run) \
                    .filter_by(id=self.__run_id) \
                    .first()

                logger.info("Cancel build '%d'", self.__build_id)
                builder.cancel()
                logger.info("Set status of build '%d' to 'stopped'", self.__build_id)
                build.status = BuildStatus.stopped
                run.status = BuildStatus.stopped
                session.commit()
                self.__redis_client.publish_build_update(build)
                self.__build_id = None
                return True
        except OperationalError as e:
            logger.error("Failed query and stop cancelled builds: %s", e)
            return False

    def __trigger_scheduler(self):
        logger.info('Trigger scheduler: process commits')
        if not self.__scheduler.process_commits():
            logger.error("Failed to trigger scheduler")
