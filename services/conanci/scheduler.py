from conanci import database
from conanci.config import app, db
from conanci.swagger_client import AgentApi, ApiClient, Configuration

import os

logger = app.app.logger

linux_agent_url = os.environ.get('CONANCI_LINUXAGENT_URL', '127.0.0.1')
linux_agent_configuration = Configuration()
linux_agent_configuration.host = "http://{0}:8080".format(linux_agent_url)
linux_agent = AgentApi(ApiClient(linux_agent_configuration))

windows_agent_url = os.environ.get('CONANCI_WINDOWSAGENT_URL', '127.0.0.1')
windows_agent_configuration = Configuration()
windows_agent_configuration.host = "http://{0}:8080".format(windows_agent_url)
windows_agent = AgentApi(ApiClient(windows_agent_configuration))


def process_commits():
    logger.info("Start processing commits")

    new_builds = False
    commits = database.Commit.query.filter_by(status=database.CommitStatus.new)
    profiles = database.Profile.query.all()
    for commit in commits:
        logger.info("Process commit '%s' of repo '%s'", commit.sha[:7], commit.repo.url)
        for profile in profiles:
            new_builds = True
            logger.info("Schedule build for '%s' with profile '%s'", commit.sha[:7], profile.name)
            build = database.Build()
            build.profile = profile
            build.commit = commit
            build.status = database.BuildStatus.new
            db.session.add(build)
        logger.info("Set commit '%s' to 'building'", commit.sha[:7])
        commit.status = database.CommitStatus.building
        db.session.commit()

    if new_builds:
        logger.info("Finish processing commits with *new* builds")
        logger.info('Trigger linux agent: process builds')
        linux_agent.process_builds()
        logger.info('Trigger windows agent: process builds')
        windows_agent.process_builds()
    else:
        logger.info("Finish processing commits with *no* builds")

    return new_builds
