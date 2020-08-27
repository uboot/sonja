import connexion
import six

from swagger_server.models.profile import Profile  # noqa: E501
from swagger_server.models.repo import Repo  # noqa: E501
from swagger_server import util


def add_profile(body=None):  # noqa: E501
    """add a new profile

     # noqa: E501

    :param body: profile to add
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = Profile.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def add_repo(body=None):  # noqa: E501
    """add a new repo

     # noqa: E501

    :param body: repo to add
    :type body: dict | bytes

    :rtype: Repo
    """
    if connexion.request.is_json:
        body = Repo.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def delete_profile(profile_id):  # noqa: E501
    """delete a profile

     # noqa: E501

    :param profile_id: profile id to delete
    :type profile_id: int

    :rtype: None
    """
    return 'do some magic!'


def delete_repo(repo_id):  # noqa: E501
    """delete a repo

     # noqa: E501

    :param repo_id: repo id to delete
    :type repo_id: int

    :rtype: None
    """
    return 'do some magic!'


def get_profiles():  # noqa: E501
    """get all active profiles

     # noqa: E501


    :rtype: List[Profile]
    """
    return 'do some magic!'


def get_repos():  # noqa: E501
    """get all current repos

     # noqa: E501


    :rtype: List[Repo]
    """
    return 'do some magic!'


def update_profile(body=None):  # noqa: E501
    """update an existing profile

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: Profile
    """
    if connexion.request.is_json:
        body = Profile.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'


def update_repo(body=None):  # noqa: E501
    """update an existing repo

     # noqa: E501

    :param body: 
    :type body: dict | bytes

    :rtype: Repo
    """
    if connexion.request.is_json:
        body = Repo.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
