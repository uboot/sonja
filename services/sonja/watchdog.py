from sonja.config import connect_to_database, logger
from sonja.client import WindowsAgent, LinuxAgent
from sonja.database import session_scope
from sonja.model import Build, Run, BuildStatus, RunStatus
from sonja.redis import RedisClient
from sonja.worker import Worker
from datetime import datetime, timedelta

WATCHDOG_PERIOD_SECONDS = 60


class Watchdog(Worker):
    def __init__(self, linux_agent: LinuxAgent, windows_agent: WindowsAgent, redis_client: RedisClient):
        super().__init__()
        connect_to_database()
        self.__linux_agent = linux_agent
        self.__windows_agent = windows_agent
        self.__redis_client = redis_client

    async def work(self):
        try:
            self.__process_stalled_runs()
        except Exception as e:
            logger.error("Watchdog failed: %s", e)
        self.reschedule_internally(WATCHDOG_PERIOD_SECONDS)

    def __process_stalled_runs(self):
        with session_scope() as session:
            # query all stalled runs of active builds
            runs = session.query(Run)\
                .join(Run.build)\
                .filter(Run.updated < datetime.utcnow() - timedelta(seconds=60),
                        Build.status == BuildStatus.active).all()
            updated_builds = []
            for run in runs:
                updated_builds.append(run.build)
                logger.info("Set run '%d' to stalled, reschedule build '%d'", run.id, run.build.id)
                run.status = RunStatus.stalled
                run.build.status = BuildStatus.new
            builds_were_restarted = len(updated_builds) > 0

            # query all stalled runs of stopping builds
            runs = session.query(Run)\
                .join(Run.build)\
                .filter(Run.updated < datetime.utcnow() - timedelta(seconds=60),
                        Build.status == BuildStatus.stopping).all()
            for run in runs:
                updated_builds.append(run.build)
                logger.info("Set run '%d' to stalled, stop build '%d'", run.id, run.build.id)
                run.status = RunStatus.stalled
                run.build.status = BuildStatus.stopped

            if len(updated_builds):
                self.__redis_client.publish_build_updates(updated_builds)

        if builds_were_restarted:
            logger.info('Trigger linux agent: process builds')
            if not self.__linux_agent.process_builds():
                logger.error("Failed to trigger Linux agent")

            logger.info('Trigger windows agent: process builds')
            if not self.__windows_agent.process_builds():
                logger.error("Failed to trigger Windows agent")