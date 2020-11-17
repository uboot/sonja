import connexion
import six

from conanci.agent import Agent
from conanci.config import app

agent = Agent()
logger = app.app.logger


def ping():  # noqa: E501
    """ping the service

     # noqa: E501


    :rtype: None
    """
    return 'success'

def process_builds():  # noqa: E501
    """Process new builds

     # noqa: E501


    :rtype: None
    """
    logger.info('Process builds')
    agent.trigger()
    return 'success'
