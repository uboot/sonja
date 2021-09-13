import base64
import os

from flask_login import current_user, LoginManager, UserMixin


secret_key = os.environ.get('CONANCI_SECRET_KEY', 'MDAwMDAwMDAwMDAwMDAwMA==')


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


def restore(user):
    return current_user.id == user and current_user.is_authenticated


def get_user() -> str:
    if current_user:
        return current_user.id

    return None