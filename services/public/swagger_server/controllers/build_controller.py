import connexion
import os

from conanci import database
from conanci.config import logger
from conanci.swagger_client import ApiClient, Configuration, AgentApi
from flask import abort
from swagger_server import models
from urllib3.exceptions import MaxRetryError

linux_agent_url = os.environ.get('CONANCI_LINUXAGENT_URL', '127.0.0.1')
linux_agent_configuration = Configuration()
linux_agent_configuration.host = "http://{0}:8080".format(linux_agent_url)
linux_agent = AgentApi(ApiClient(linux_agent_configuration))

windows_agent_url = os.environ.get('CONANCI_WINDOWSAGENT_URL', '127.0.0.1')
windows_agent_configuration = Configuration()
windows_agent_configuration.host = "http://{0}:8080".format(windows_agent_url)
windows_agent = AgentApi(ApiClient(windows_agent_configuration))

build_status_table = {
    "new": database.BuildStatus.new,
    "active": database.BuildStatus.active,
    "error": database.BuildStatus.error,
    "stopping": database.BuildStatus.stopping,
    "stopped": database.BuildStatus.stopped,
    "success": database.BuildStatus.success
}


def __create_build(record: database.Build):
    return models.Build(
        id=record.id,
        type="builds",
        attributes=models.BuildAttributes(
            status=record.status.name
        ),
        relationships=models.BuildRelationships(
            ecosystem=models.RepoRelationshipsEcosystem(
                models.RepoRelationshipsEcosystemData(
                    id=record.profile.ecosystem_id,
                    type="ecosystems"
                )
            ),
            commit=models.BuildRelationshipsCommit(
                data=models.BuildRelationshipsCommitData(
                    id=record.commit_id,
                    type="commits"
                )
            ),
            profile=models.BuildRelationshipsProfile(
                data=models.EcosystemRelationshipsProfilesData(
                    id=record.profile_id,
                    type="profiles"
                )
            ),
            log=models.BuildRelationshipsLog(
                data=models.BuildRelationshipsLogData(
                    id=record.log_id,
                    type="logs"
                )
            ),
            package=models.BuildRelationshipsPackage(
                data=models.BuildRelationshipsPackageData(
                    id=record.package_id,
                    type="packages"
                )
            )
        )
    )


def get_build(build_id):
    with database.session_scope() as session:
        record = session.query(database.Build).filter_by(id=build_id).first()
        if not record:
            abort(404)
        return models.BuildData(data=__create_build(record))


def get_builds(ecosystem_id):
    with database.session_scope() as session:
        # try:
        #     status = build_status_table[filter_status]
        # except KeyError:
        #     abort(400)
        records = session.query(database.Build).\
            join(database.Build.profile).\
            filter(database.Profile.ecosystem_id == ecosystem_id)
        return models.BuildList(data=[__create_build(record) for record in records])


def update_build(build_id, body=None):
    if connexion.request.is_json:
        body = models.BuildData.from_dict(connexion.request.get_json())  # noqa: E501

    with database.session_scope() as session:
        record = session.query(database.Build).filter_by(id=build_id).first()
        if not record:
            abort(404)
        try:
            record.status = build_status_table[body.data.attributes.status]
            if record.status == database.BuildStatus.new:
                log = record.log
                record.log = None
                session.delete(log)

                logger.info('Trigger linux agent: process builds')
                try:
                    linux_agent.process_builds()
                except MaxRetryError:
                    logger.error("Failed to trigger Linux agent")

                logger.info('Trigger windows agent: process builds')
                try:
                    windows_agent.process_builds()
                except MaxRetryError:
                    logger.error("Failed to trigger Windows agent")
        except KeyError:
            abort(400)

        return models.BuildData(data=__create_build(record))
