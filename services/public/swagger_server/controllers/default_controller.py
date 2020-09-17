import connexion
import six

from flask import abort
from swagger_server.config import db
from swagger_server import database
from swagger_server.models.channel import Channel  # noqa: E501
from swagger_server.models.profile import Profile  # noqa: E501
from swagger_server.models.setting import Setting  # noqa: E501
from swagger_server.models.repo import Repo  # noqa: E501
from swagger_server import util

def add_channel(body=None):  # noqa: E501
    """add a new channel

     # noqa: E501

    :param body: channel to add
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = Channel.from_dict(connexion.request.get_json())  # noqa: E501
        channel = database.Channel()
        channel.name = body.name
        channel.branch = body.branch
        db.session.add(channel)
        db.session.commit()
        body.id = channel.id

    return body, 201

def add_profile(body=None):  # noqa: E501
    """add a new profile

     # noqa: E501

    :param body: profile to add
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = Profile.from_dict(connexion.request.get_json())  # noqa: E501
        profile = database.Profile()
        profile.name = body.name
        profile.container = body.container
        profile.settings = [database.Setting(s.key, s.value) for s in body.settings]
        db.session.add(profile)
        db.session.commit()
        body.id = profile.id

    return body, 201


def add_repo(body=None):  # noqa: E501
    """add a new repo

     # noqa: E501

    :param body: repo to add
    :type body: dict | bytes

    :rtype: Repo
    """
    if connexion.request.is_json:
        body = Repo.from_dict(connexion.request.get_json())  # noqa: E501
        repo = database.Repo()
        repo.path = body.path
        repo.url = body.url
        db.session.add(repo)
        db.session.commit()
        body.id = repo.id

    return body, 201


def delete_channel(channel_id):  # noqa: E501
    """delete a channel

     # noqa: E501

    :param channel_id: channel id to delete
    :type channel_id: int

    :rtype: None
    """
    channel = database.Channel.query.filter_by(id=channel_id).first()
    if not channel:
        abort(404)
    db.session.delete(channel)
    db.session.commit()
    return None


def delete_profile(profile_id):  # noqa: E501
    """delete a profile

     # noqa: E501

    :param profile_id: profile id to delete
    :type profile_id: int

    :rtype: None
    """
    profile = database.Profile.query.filter_by(id=profile_id).first()
    if not profile:
        abort(404)
    db.session.delete(profile)
    db.session.commit()
    return None


def delete_repo(repo_id):  # noqa: E501
    """delete a repo

     # noqa: E501

    :param repo_id: repo id to delete
    :type repo_id: int

    :rtype: None
    """
    repo = database.Repo.query.filter_by(id=repo_id).first()
    if not repo:
        abort(404)
    db.session.delete(repo)
    db.session.commit()
    return None


def get_channels():  # noqa: E501
    """get all channels

     # noqa: E501


    :rtype: List[Channel]
    """
    return [Channel(c.id, c.name, c.branch) for c in database.Channel.query.all()]



def get_profiles():  # noqa: E501
    """get all active profiles

     # noqa: E501


    :rtype: List[Profile]
    """
    return [Profile(p.id, p.name, p.container, [Setting(s.key, s.value) for s in p.settings]) for p in database.Profile.query.all()]


def get_repos():  # noqa: E501
    """get all current repos

     # noqa: E501


    :rtype: List[Repo]
    """
    return [Repo(r.id, r.url, r.path) for r in database.Repo.query.all()]
