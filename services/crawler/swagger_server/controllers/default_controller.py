import connexion
import os
import six

from conanci import crawler
from conanci.config import app
from swagger_server import util

logger = app.app.logger


def ping():  # noqa: E501
    """ping the service

     # noqa: E501


    :rtype: None
    """
    return 'success'

def process_repos():  # noqa: E501
    """scan repos for new commits

     # noqa: E501


    :rtype: None
    """
    crawler.process_repos()
    return 'success'
