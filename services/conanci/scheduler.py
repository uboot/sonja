import asyncio
from conanci import database
from conanci.config import connect_to_database, logger
from conanci.worker import Worker
from urllib3.exceptions import MaxRetryError


class Scheduler(Worker):
    def __init__(self, linux_agent, windows_agent):
        super().__init__()
        connect_to_database()
        self.__linux_agent = linux_agent
        self.__windows_agent = windows_agent

    async def work(self):
        new_commits = True
        while new_commits:
            new_commits = await self.__process_commits()
        self.reschedule(60)
        
    async def __process_commits(self):
        logger.info("Start processing commits")

        new_commits = False
        with database.session_scope() as session:
            commits = session.query(database.Commit).filter_by(status=database.CommitStatus.new)
            profiles = session.query(database.Profile).all()
            for commit in commits:
                logger.info("Process commit '%s' of repo '%s'", commit.sha[:7], commit.repo.url)
                for profile in profiles:
                    new_commits = True
                    logger.info("Schedule build for '%s' with profile '%s'", commit.sha[:7], profile.name)
                    build = database.Build()
                    build.profile = profile
                    build.commit = commit
                    build.status = database.BuildStatus.new
                    session.add(build)
                logger.info("Set commit '%s' to 'building'", commit.sha[:7])
                commit.status = database.CommitStatus.building

        if new_commits:
            logger.info("Finish processing commits with *new* builds")
        else:
            logger.info("Finish processing commits with *no* builds")

        with database.session_scope() as session:
            num_new_builds = session.query(database.Build).filter_by(status=database.BuildStatus.new).count()
        logger.info("Currently %d new builds exist", num_new_builds)

        if num_new_builds == 0:
            return new_commits

        logger.info('Trigger linux agent: process builds')
        try:
            self.__linux_agent.process_builds()
        except MaxRetryError:
            logger.error("Failed to trigger Linux agent")

        logger.info('Trigger windows agent: process builds')
        try:
            self.__windows_agent.process_builds()
        except MaxRetryError:
            logger.error("Failed to trigger Windows agent")

        return new_commits

