import connexion
import six

from conanci import scheduler
from conanci.config import app
from swagger_server import util

logger = app.app.logger


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
