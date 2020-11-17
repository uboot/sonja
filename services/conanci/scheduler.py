from conanci import database
from conanci.config import app, connect_to_database
from conanci.worker import Worker

import os

logger = app.app.logger


class Scheduler(Worker):
    def __init__(self, linux_agent, windows_agent):
        super().__init__()
        connect_to_database()
        self.__linux_agent = linux_agent
        self.__windows_agent = windows_agent

    async def work(self):
        logger.info("Start processing commits")

        with database.session_scope() as session:
            new_builds = False
            commits = session.query(database.Commit).filter_by(status=database.CommitStatus.new)
            profiles = session.query(database.Profile).all()
            for commit in commits:
                logger.info("Process commit '%s' of repo '%s'", commit.sha[:7], commit.repo.url)
                for profile in profiles:
                    new_builds = True
                    logger.info("Schedule build for '%s' with profile '%s'", commit.sha[:7], profile.name)
                    build = database.Build()
                    build.profile = profile
                    build.commit = commit
                    build.status = database.BuildStatus.new
                    session.add(build)
                logger.info("Set commit '%s' to 'building'", commit.sha[:7])
                commit.status = database.CommitStatus.building

            if new_builds:
                logger.info("Finish processing commits with *new* builds")
                logger.info('Trigger linux agent: process builds')
                self.__linux_agent.process_builds()
                logger.info('Trigger windows agent: process builds')
                self.__windows_agent.process_builds()
            else:
                logger.info("Finish processing commits with *no* builds")

            return new_builds
