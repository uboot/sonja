from conanci.config import app, connect_to_database, setup_logging
from swagger_server import encoder, auth
import os.path

swagger_api = os.path.join(os.path.dirname(__file__), 'swagger', 'swagger.yaml')


def create_app():
    app.add_api(swagger_api, arguments={'title': 'Conan CI Public API'}, pythonic_params=True)
    app.app.json_encoder = encoder.JSONEncoder
    setup_logging()
    auth.setup_login(app.app)
    connect_to_database()
    return app
