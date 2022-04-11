from sonja.config import connect_to_database, logger
from sonja.client import WindowsAgent, LinuxAgent
from sonja.redis import RedisClient
from sonja.database import session_scope
from sonja.model import Build, BuildStatus, CommitStatus, Log, Profile, Commit
from sonja.worker import Worker
import time


SCHEDULER_PERIOD_SECONDS = 60
TIMEOUT = 10


class Scheduler(Worker):
    def __init__(self, linux_agent: LinuxAgent, windows_agent: WindowsAgent, redis_client: RedisClient):
        super().__init__()
        connect_to_database()
        self.__linux_agent = linux_agent
        self.__windows_agent = windows_agent
        self.__redis_client = redis_client

    async def work(self):
        new_commits = True
        while new_commits:
            try:
                new_commits = await self.__process_commits()
            except Exception as e:
                logger.error("Processing commits failed: %s", e)
                logger.info("Retry in %i seconds", TIMEOUT)
                time.sleep(TIMEOUT)
        #self.reschedule_internally(SCHEDULER_PERIOD_SECONDS)
        
    async def __process_commits(self):
        logger.info("Start processing commits")

        new_commits = False
        with session_scope() as session:
            new_builds = []
            commits = session.query(Commit).filter_by(status=CommitStatus.new)
            profiles = session.query(Profile).all()
            for commit in commits:
                logger.info("Process commit '%s' of repo '%s'", commit.sha[:7], commit.repo.url)
                exclude_labels = {label.value for label in commit.repo.exclude}
                for profile in profiles:
                    labels = {label.value for label in profile.labels}
                    if not labels.isdisjoint(exclude_labels):
                        logger.info("Exclude build for '%s' with profile '%s'", commit.sha[:7], profile.name)
                        continue

                    new_commits = True
                    logger.info("Schedule build for '%s' with profile '%s'", commit.sha[:7], profile.name)
                    build = Build()
                    build.profile = profile
                    build.commit = commit
                    build.status = BuildStatus.new
                    build.log = Log()
                    build.log.logs = ''
                    session.add(build)
                    new_builds.append(build)
                logger.info("Set commit '%s' to 'building'", commit.sha[:7])
                commit.status = CommitStatus.building

            session.commit()
            if new_builds:
                self.__redis_client.publish_build_updates(new_builds)

        if new_commits:
            logger.info("Finish processing commits with *new* builds")
        else:
            logger.info("Finish processing commits with *no* builds")

        with session_scope() as session:
            num_new_builds = session.query(Build).filter_by(status=BuildStatus.new).count()
        logger.info("Currently %d new builds exist", num_new_builds)

        if num_new_builds == 0:
            return new_commits

        logger.info('Trigger linux agent: process builds')
        if not self.__linux_agent.process_builds():
            logger.error("Failed to trigger Linux agent")

        logger.info('Trigger windows agent: process builds')
        if not self.__windows_agent.process_builds():
            logger.error("Failed to trigger Windows agent")

        return new_commits
