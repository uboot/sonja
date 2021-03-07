from flask_login import LoginManager, UserMixin


class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id


def setup_login(app):
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id)