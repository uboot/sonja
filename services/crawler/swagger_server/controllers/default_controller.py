import connexion
import os
import six

from conanci.crawler import Crawler
from conanci.config import app
from conanci.swagger_client import SchedulerApi, ApiClient, Configuration

scheduler_url = os.environ.get('CONANCI_SCHEDULER_URL', '127.0.0.1')
configuration = Configuration()
configuration.host = "http://{0}:8080".format(scheduler_url)
scheduler = SchedulerApi(ApiClient(configuration))

crawler = Crawler(scheduler)
logger = app.app.logger


def ping():  # noqa: E501
    """ping the service

     # noqa: E501


    :rtype: None
    """
    return 'success'

def process_repo(repo_id):  # noqa: E501
    """scan repos for new commits

     # noqa: E501


    :rtype: None
    """
    crawler.post_repo(repo_id)
    crawler.trigger()
    return 'success'
