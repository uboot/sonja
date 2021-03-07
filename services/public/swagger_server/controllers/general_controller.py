import connexion
import os

from conanci import database
from conanci.swagger_client import ApiClient, Configuration, CrawlerApi
from flask_login import login_user
from urllib3.exceptions import MaxRetryError
from swagger_server import auth, models


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


def login(body=None):  # noqa: E501
    """log in

     # noqa: E501

    :param body: login credentials
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = models.Credentials.from_dict(connexion.request.get_json())  # noqa: E501

    user = auth.User(body.user)
    login_user(user)

    return 'do some magic!'


def logout():  # noqa: E501
    """log out

     # noqa: E501


    :rtype: None
    """
    return 'do some magic!'


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
    try:
        crawler.process_repos()
    except MaxRetryError as e:
        pass
    return 'success'
