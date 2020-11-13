import connexion
import os
import six

from conanci.scheduler import Scheduler
from conanci.config import app
from conanci.swagger_client import AgentApi, ApiClient, Configuration
from swagger_server import util

logger = app.app.logger

linux_agent_url = os.environ.get('CONANCI_LINUXAGENT_URL', '127.0.0.1')
linux_agent_configuration = Configuration()
linux_agent_configuration.host = "http://{0}:8080".format(linux_agent_url)
linux_agent = AgentApi(ApiClient(linux_agent_configuration))

windows_agent_url = os.environ.get('CONANCI_WINDOWSAGENT_URL', '127.0.0.1')
windows_agent_configuration = Configuration()
windows_agent_configuration.host = "http://{0}:8080".format(windows_agent_url)
windows_agent = AgentApi(ApiClient(windows_agent_configuration))

scheduler = Scheduler(linux_agent, windows_agent)


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
    scheduler.process_commits()
    return 'success'

def process_packages():  # noqa: E501
    """Process new packages

     # noqa: E501


    :rtype: None
    """
    return 'do some magic!'
