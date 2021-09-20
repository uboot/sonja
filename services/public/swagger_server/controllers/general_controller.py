import connexion
import os

from sonja import database
from sonja.swagger_client import ApiClient, Configuration, CrawlerApi
from sonja.ssh import test_password
from flask import abort
from flask_login import login_user, logout_user
from urllib3.exceptions import MaxRetryError
from swagger_server import auth, models


crawler_url = os.environ.get('SONJA_CRAWLER_URL', '127.0.0.1')
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

    with database.session_scope() as session:
        record = session.query(database.User).filter_by(user_name=body.user_name).first()
        if not record:
            abort(401, 'Wrong credentials')
        if not test_password(body.password, record.password):
            abort(401, 'Wrong credentials')

        user = auth.User(str(record.id))

    login_user(user)

    return models.UserToken(user_id=auth.get_user()), 200


def logout():  # noqa: E501
    """log out

     # noqa: E501


    :rtype: None
    """

    logout_user();
    return 'logged out', 200


def restore(body=None):  # noqa: E501
    """restore session

     # noqa: E501

    :param body: user data
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = models.UserToken.from_dict(connexion.request.get_json())  # noqa: E501

    if body.user_id != auth.get_user():
        abort(401, 'Token does not match current user')

    return models.UserToken(user_id=auth.get_user()), 200


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


def process_repo(repo_id):  # noqa: E501
    """scan repos for new commits

     # noqa: E501

    :param repo_id: repo ID
    :type repo_id: str

    :rtype: None
    """
    try:
        crawler.process_repo(repo_id)
    except MaxRetryError as e:
        pass
    return 'success'

