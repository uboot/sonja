import connexion
import six

from swagger_server.models.build import Build  # noqa: E501
from swagger_server import util


def schedule_build(body=None):  # noqa: E501
    """schedule a build

     # noqa: E501

    :param body: build to schedule
    :type body: dict | bytes

    :rtype: None
    """
    if connexion.request.is_json:
        body = Build.from_dict(connexion.request.get_json())  # noqa: E501
    return 'do some magic!'
