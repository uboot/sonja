import connexion
import logging
import os

from sonja.database import reset_database, session_scope
from sonja.test import util
from flask import json
from flask_testing import TestCase
from swagger_server import auth, encoder, models

swagger_api = os.path.join(os.path.dirname(__file__),'..', 'swagger', 'swagger.yaml')

class BaseTestCase(TestCase):

    def create_app(self):
        logging.getLogger('connexion.operation').setLevel('ERROR')
        app = connexion.App(__name__, specification_dir='../swagger/')
        app.app.json_encoder = encoder.JSONEncoder
        app.add_api(swagger_api, arguments={'title': 'Linux Agent'}, pythonic_params=True)
        auth.setup_login(app.app)
        return app.app

    def setUp(self):
        reset_database()

    def login(self):
        with session_scope() as session:
            user = util.create_user(dict())
            session.add(user)

        body = models.Credentials(user_name="user", password="password")
        self.client.open(
            '/api/v1/login',
            method='POST',
            data=json.dumps(body),
            content_type='application/json')

    def assert201(self, response, message=None):
        self.assertStatus(response, 201, message)

    def assert204(self, response, message=None):
        self.assertStatus(response, 204, message)

    def assert409(self, response, message=None):
        self.assertStatus(response, 409, message)
