from sqlalchemy import create_engine, Column, Enum, ForeignKey, Integer, String, Table
from sqlalchemy.orm import backref, relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from contextlib import contextmanager
import enum
import logging
import os


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("conanci")


# start MySQL:
# docker run --rm -d --name mysql -p 3306:3306 -e MYSQL_DATABASE=conan-ci -e MYSQL_ROOT_PASSWORD=secret mysql:8.0.21
# docker run --rm -d --name phpmyadmin --link mysql:db -p 8081:80 phpmyadmin:5.0.4

connection_string = 'mysql+mysqldb://root:{0}@{1}/conan-ci'.format(
    os.environ.get('MYSQL_ROOT_PASSWORD', 'secret'),
    os.environ.get('MYSQL_URL', '127.0.0.1')
)
Base = declarative_base()
engine = create_engine(connection_string, echo=False)
Session = sessionmaker(engine)


class Repo(Base):
    __tablename__ = 'repo'

    id = Column(Integer, primary_key=True)
    url = Column(String(255), nullable=False)
    path = Column(String(255))


class Channel(Base):
    __tablename__ = 'channel'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    branch = Column(String(255), nullable=False)


class Profile(Base):
    __tablename__ = 'profile'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    container = Column(String(255), nullable=False)
    settings = relationship('Setting', backref='profile', lazy=True,
                               cascade="all, delete, delete-orphan")


class Setting(Base):
    __tablename__ = 'setting'

    id = Column(Integer, primary_key=True)
    key = Column(String(255), nullable=False)
    value = Column(String(255), nullable=False)
    profile_id = Column(Integer, ForeignKey('profile.id'),
                           nullable=False)

    def __init__(self, key, value):
        self.key = key
        self.value = value


class CommitStatus(enum.Enum):
    new = 1
    building = 2
    old = 3


class Commit(Base):
    __tablename__ = 'commit'

    id = Column(Integer, primary_key=True)
    status = Column(Enum(CommitStatus), nullable=False)
    sha = Column(String(255), nullable=False)
    repo_id = Column(Integer, ForeignKey('repo.id'),
                        nullable=False)
    repo = relationship('Repo', backref='commits')
    channel_id = Column(Integer, ForeignKey('channel.id'),
                           nullable=False)
    channel = relationship('Channel', backref='commits')


class BuildStatus(enum.Enum):
    new = 1
    active = 2
    error = 3
    success = 4
    stopping = 5
    stopped = 6


dependencies = Table('dependencies', Base.metadata,
    Column('package_id', Integer, ForeignKey('package.id'), primary_key=True),
    Column('build_id', Integer, ForeignKey('build.id'), primary_key=True)
)

missing = Table('missing', Base.metadata,
    Column('pattern_id', Integer, ForeignKey('pattern.id'), primary_key=True),
    Column('build_id', Integer, ForeignKey('build.id'), primary_key=True)
)


class Build(Base):
    __tablename__ = 'build'

    id = Column(Integer, primary_key=True)
    status = Column(Enum(BuildStatus), nullable=False)
    commit_id = Column(Integer, ForeignKey('commit.id'),
                          nullable=False)
    commit = relationship('Commit', backref='builds')
    package_id = Column(Integer, ForeignKey('package.id'))
    package = relationship("Package", backref="builds")
    profile_id = Column(Integer, ForeignKey('profile.id'), nullable=False)
    profile = relationship("Profile")
    dependencies = relationship('Package', secondary=dependencies,
        backref=backref('dependencies'))
    missing = relationship('Pattern', secondary=missing,
        backref=backref('missing'))


class Package(Base):
    __tablename__ = 'package'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    version = Column(String(255), nullable=False)
    recipe_revision = Column(String(255), nullable=False)
    package_revision = Column(String(255), nullable=False)
    

class Pattern(Base):
    __tablename__ = 'pattern'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    version = Column(String(255), nullable=False)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def populate_database():
    logger.info("Populate database")
    with session_scope() as session:
        repo = Repo()
        repo.url = "git@github.com:uboot/conan-ci.git"
        repo.path = "packages/hello"
        session.add(repo)

        linux = Profile()
        linux.name = "GCC 9"
        linux.container = "uboot/gcc9:latest"
        linux.settings = [
            Setting("os", "Linux"),
            Setting("build_type", "Release")
        ]
        session.add(linux)

        windows = Profile()
        windows.name = "MSVC 15"
        windows.container = "msvc15:local"
        windows.settings = [
            Setting("os", "Windows"),
            Setting("build_type", "Release")
        ]
        session.add(windows)

        channel = Channel()
        channel.branch = "master"
        channel.name = "stable"
        session.add(channel)

        # commit = Commit()
        # commit.repo = repo
        # commit.sha = "2777a37dc82e296d55c23f738b79f139e627920c"
        # commit.channel = channel
        # commit.status = CommitStatus.new

        # linux_build = Build()
        # linux_build.commit = commit
        # linux_build.profile = linux
        # linux_build.status = BuildStatus.new
        # session.add(linux_build)

        # windows_build = Build()
        # windows_build.commit = commit
        # windows_build.profile = windows
        # windows_build.status = BuildStatus.new
        # session.add(windows_build)

        session.commit()


def clear_database():
    with session_scope() as session:
        session.query(Build).delete()
        session.query(Commit).delete()
        session.query(Channel).delete()
        session.query(Setting).delete()
        session.query(Profile).delete()
        session.query(Repo).delete()