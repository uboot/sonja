import connexion
import six

from conanci import scheduler
from conanci.config import app
import swagger_client
from swagger_server import util

logger = app.app.logger
linux_agent = swagger_client.DefaultApi(swagger_client.ApiClient(None))


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
    return 'success'

def process_packages():  # noqa: E501
    """Process new packages

     # noqa: E501


    :rtype: None
    """
    return 'do some magic!'
