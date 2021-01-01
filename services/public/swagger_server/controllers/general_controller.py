import os

from conanci import database
from conanci.swagger_client import ApiClient, Configuration, CrawlerApi


crawler_url = os.environ.get('CONANCI_CRAWLER_URL', '127.0.0.1')
crawler_configuration = Configuration()
crawler_configuration.host = "http://{0}:8080".format(crawler_url)
crawler = CrawlerApi(ApiClient(crawler_configuration))


def clear_database():  # noqa: E501
    """remove all entries from the database

     # noqa: E501


    :rtype: None
    """
    database.clear_database()
    return 'success'


def clear_ecosystems():  # noqa: E501
    """remove all entries but the ecosystems from the database

     # noqa: E501


    :rtype: None
    """
    database.clear_ecosystems()
    return 'success'


def ping():  # noqa: E501
    """ping the service

     # noqa: E501


    :rtype: None
    """
    return 'success'


def populate_database():  # noqa: E501
    """populate the database with sample data

     # noqa: E501


    :rtype: None
    """
    database.populate_database()
    return 'success'


def process_repos():  # noqa: E501
    """scan repos for new commits

     # noqa: E501


    :rtype: None
    """
    crawler.process_repos()
    return 'success'
