import connexion
import os
import six

from conanci import scheduler
from conanci.config import app
from swagger_client import DefaultApi, ApiClient, Configuration
from swagger_server import util

logger = app.app.logger

linux_agent_url = os.environ.get('CONANCI_LINUXAGENT_URL', '127.0.0.1')
linux_agent_configuration = Configuration()
linux_agent_configuration.host = "http://{0}:8080".format(linux_agent_url)
linux_agent = DefaultApi(ApiClient(linux_agent_configuration))

windows_agent_url = os.environ.get('CONANCI_WINDOWSAGENT_URL', '127.0.0.1')
windows_agent_configuration = Configuration()
windows_agent_configuration.host = "http://{0}:8080".format(windows_agent_url)
windows_agent = DefaultApi(ApiClient(windows_agent_configuration))


def ping():  # noqa: E501
    """ping the service

     # noqa: E501


    :rtype: None
    """
    return 'success'

def process_commits():  # noqa: E501
    """Process new commits

     # noqa: E501


    :rtype: None
    """
    if scheduler.process_commits():
        logger.info('Trigger linux agent: process builds')
        linux_agent.process_builds()
        logger.info('Trigger windows agent: process builds')
        windows_agent.process_builds()

    return 'success'

def process_packages():  # noqa: E501
    """Process new packages

     # noqa: E501


    :rtype: None
    """
    return 'do some magic!'
