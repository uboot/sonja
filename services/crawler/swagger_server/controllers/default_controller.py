import connexion
import six

import swagger_client
from swagger_server import crawler
from swagger_server import util
from swagger_server.config import app

logger = app.app.logger
scheduler = swagger_client.DefaultApi(swagger_client.ApiClient(None))


def process_repos():  # noqa: E501
    """scan repos for new commits

     # noqa: E501


    :rtype: None
    """
    if crawler.process_repos():
        logger.info('trigger scheduler: process commits')
        scheduler.process_commits()
    return 'success'
