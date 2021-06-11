import connexion
import logging
import os

from conanci.database import reset_database
from flask import json
from flask_testing import TestCase
from swagger_server import auth, encoder, models

swagger_api = os.path.join(os.path.dirname(__file__),'..', 'swagger', 'swagger.yaml')

class BaseTestCase(TestCase):

    def create_app(self):
        logging.getLogger('connexion.operation').setLevel('ERROR')
        app = connexion.App(__name__, specification_dir='../swagger/')
        app.app.json_encoder = encoder.JSONEncoder
        app.add_api(swagger_api, arguments={'title': 'Conan CI Linux Agent'}, pythonic_params=True)
        auth.master_password = 'paSSwOrd'
        auth.secret_key = 'MDAwMDAwMDAwMDAwMDAwMA=='
        auth.setup_login(app.app)
        return app.app

    def setUp(self):
        reset_database()

    def login(self):
        body = models.Credentials(user="user", password="paSSwOrd")
        self.client.open(
            '/api/v1/login',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')

    def assert201(self, response, message=None):
        self.assertStatus(response, 201, message)

    def assert204(self, response, message=None):
        self.assertStatus(response, 204, message)
