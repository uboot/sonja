from conanci.config import db
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
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'),
                           nullable=False)

    def __init__(self, key, value):
        self.key = key
        self.value = value


class CommitStatus(enum.Enum):
    new = 1
    building = 2
    old = 3


class Commit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Enum(CommitStatus), nullable=False)
    sha = db.Column(db.String(255), nullable=False)
    repo_id = db.Column(db.Integer, db.ForeignKey('repo.id'),
                        nullable=False)
    repo = db.relationship('Repo', backref='commits')
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'),
                           nullable=False)
    channel = db.relationship('Channel', backref='commits')


class BuildStatus(enum.Enum):
    new = 1
    active = 2
    error = 3
    success = 4

dependencies = db.Table('dependencies',
    db.Column('package_id', db.Integer, db.ForeignKey('package.id'), primary_key=True),
    db.Column('build_id', db.Integer, db.ForeignKey('build.id'), primary_key=True)
)

missing = db.Table('missing',
    db.Column('pattern_id', db.Integer, db.ForeignKey('pattern.id'), primary_key=True),
    db.Column('build_id', db.Integer, db.ForeignKey('build.id'), primary_key=True)
)


class Build(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Enum(BuildStatus), nullable=False)
    commit_id = db.Column(db.Integer, db.ForeignKey('commit.id'),
                          nullable=False)
    commit = db.relationship('Commit', backref='builds')
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'))
    package = db.relationship("Package", backref="builds")
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'), nullable=False)
    profile = db.relationship("Profile")
    dependencies = db.relationship('Package', secondary=dependencies,
        backref=db.backref('dependencies'))
    missing = db.relationship('Pattern', secondary=missing,
        backref=db.backref('missing'))


class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    version = db.Column(db.String(255), nullable=False)
    recipe_revision = db.Column(db.String(255), nullable=False)
    package_revision = db.Column(db.String(255), nullable=False)
    

class Pattern(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    version = db.Column(db.String(255), nullable=False)


def populate_database():
    repo = Repo()
    repo.url = "https://github.com/uboot/conan-ci.git"
    repo.path = "packages/hello"
    db.session.add(repo)

    profile = Profile()
    profile.name = "GCC 9"
    profile.container = "conanio/gcc9:1.29.2"
    profile.settings = [Setting("build_type", "Release")]
    db.session.add(profile)

    channel = Channel()
    channel.branch = "master"
    channel.name = "stable"
    db.session.add(channel)

    commit = Commit()
    commit.repo = repo
    commit.sha = "2777a37dc82e296d55c23f738b79f139e627920c"
    commit.channel = channel
    commit.status = CommitStatus.new
    build = Build()
    build.commit = commit
    build.profile = profile
    build.status = BuildStatus.new
    db.session.add(build)
    
    db.session.commit()
