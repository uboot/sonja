import base64
import os

from flask_login import LoginManager, UserMixin


master_password = os.environ.get('PASSWORD', None)
secret_key = os.environ.get('SECRET_KEY', None)


class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id


def setup_login(app):
    app.secret_key = base64.b64decode(secret_key)
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id)


def authorize(user, password):
    return password == master_password