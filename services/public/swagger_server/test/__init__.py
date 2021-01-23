import connexion
import logging
import os

from conanci.config import connect_to_database
from flask_testing import TestCase
from swagger_server import encoder

swagger_api = os.path.join(os.path.dirname(__file__),'..', 'swagger', 'swagger.yaml')

class BaseTestCase(TestCase):

    def create_app(self):
        logging.getLogger('connexion.operation').setLevel('ERROR')
        app = connexion.App(__name__, specification_dir='../swagger/')
        app.app.json_encoder = encoder.JSONEncoder
        app.add_api(swagger_api, arguments={'title': 'Conan CI Linux Agent'}, pythonic_params=True)
        connect_to_database()
        return app.app
