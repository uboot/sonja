import connexion
import six

from swagger_server import linux_agent
from swagger_server import util
from swagger_server.config import app

logger = app.app.logger


def process_builds():  # noqa: E501
    """Process new builds

     # noqa: E501


    :rtype: None
    """
    logger.info('process builds')
    linux_agent.process_builds()
    return 'success'
