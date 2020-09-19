import connexion
import six

from swagger_server import util
from swagger_server.crawler import process


def process_repos():  # noqa: E501
    """scan repos for new commits

     # noqa: E501


    :rtype: None
    """

    process.trigger()
    return 'success'
