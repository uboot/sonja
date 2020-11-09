import connexion
import os
import six

from conanci import crawler
from conanci.config import app
from swagger_client import DefaultApi, ApiClient, Configuration
from swagger_server import util

logger = app.app.logger

scheduler_url = os.environ.get('CONANCI_SCHEDULER_URL', '127.0.0.1')
configuration = Configuration()
configuration.host = "http://{0}:8080".format(scheduler_url)
scheduler = DefaultApi(ApiClient(configuration))


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
    if crawler.process_repos():
        logger.info('Trigger scheduler: process commits')
        scheduler.process_commits()
    return 'success'
