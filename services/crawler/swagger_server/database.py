from swagger_server.config import db
import enum

class Repo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(255))

class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    branch = db.Column(db.String(255), nullable=False)

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

class Commit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sha = db.Column(db.String(255), nullable=False)
    repo_id = db.Column(db.Integer, db.ForeignKey('repo.id'), nullable=False)
    repo = db.relationship("Repo")

class Status(enum.Enum):
    new = 1
    active = 2
    error = 3
    success = 4

class Build(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Enum(Status))
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'), nullable=False)
    profile = db.relationship("Profile")

class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    version = db.Column(db.String(255), nullable=False)
    recipe_revision = db.Column(db.String(255), nullable=False)
    package_revision = db.Column(db.String(255), nullable=False)
    
    



