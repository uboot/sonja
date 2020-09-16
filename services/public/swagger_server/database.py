from swagger_server.config import db

class Repo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(255))

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    container = db.Column(db.String(255), nullable=False)
    settings = db.relationship('Setting', backref='profile', lazy=True,
        cascade="all, delete, delete-orphan")

class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), nullable=False)
    value = db.Column(db.String(255), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'), nullable=False)

    def __init__(self, key, value):
        self.key = key
        self.value = value