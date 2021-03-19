from sqlalchemy import create_engine, Column, Enum, ForeignKey, Integer, String, Table, Text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship, sessionmaker

import sqlalchemy

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


class Ecosystem(Base):
    __tablename__ = 'ecosystem'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    user = Column(String(255))
    public_ssh_key = Column(Text())
    ssh_key = Column(Text())
    known_hosts = Column(Text())
    conan_remote = Column(String(255))
    conan_user = Column(String(255))
    conan_password = Column(String(255))
    settings = Column(Text())


class Repo(Base):
    __tablename__ = 'repo'

    id = Column(Integer, primary_key=True)
    ecosystem_id = Column(Integer, ForeignKey('ecosystem.id'))
    ecosystem = relationship("Ecosystem", backref="repos")
    name = Column(String(255))
    url = Column(String(255))
    path = Column(String(255))


class Channel(Base):
    __tablename__ = 'channel'

    id = Column(Integer, primary_key=True)
    ecosystem_id = Column(Integer, ForeignKey('ecosystem.id'))
    ecosystem = relationship("Ecosystem", backref="channels")
    name = Column(String(255), nullable=False)
    branch = Column(String(255))


class Profile(Base):
    __tablename__ = 'profile'

    id = Column(Integer, primary_key=True)
    ecosystem_id = Column(Integer, ForeignKey('ecosystem.id'))
    ecosystem = relationship("Ecosystem", backref="profiles")
    name = Column(String(255), nullable=False)
    container = Column(String(255))
    docker_user = Column(String(255))
    docker_password = Column(String(255))
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


def reset_database():
        try:
            Base.metadata.drop_all(engine)
            Base.metadata.create_all(engine)
            return
        except OperationalError:
            logger.warning("Failed to connect to database")
            raise


def populate_database():
    logger.info("Populate database")
    with session_scope() as session:
        ecosystem = session.query(Ecosystem).filter_by(id=1).first()
        if not ecosystem:
            raise Exception("Found no ecosystem with ID=1")

        repo = Repo()
        repo.name = "Hello"
        repo.ecosystem = ecosystem
        repo.url = "git@github.com:uboot/conan-ci.git"
        repo.path = "packages/hello"
        session.add(repo)

        linux = Profile()
        linux.ecosystem = ecosystem
        linux.name = "GCC 9"
        linux.container = "uboot/gcc9:latest"
        linux.settings = [
            Setting("os", "Linux"),
            Setting("build_type", "Release")
        ]
        session.add(linux)

        windows = Profile()
        windows.ecosystem = ecosystem
        windows.name = "MSVC 15"
        windows.container = "uboot/msvc15:latest"
        windows.settings = [
            Setting("os", "Windows"),
            Setting("build_type", "Release")
        ]
        session.add(windows)

        channel = Channel()
        channel.ecosystem = ecosystem
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
        # linux_build.status = BuildStatus.active
        # session.add(linux_build)

        # windows_build = Build()
        # windows_build.commit = commit
        # windows_build.profile = windows
        # windows_build.status = BuildStatus.active
        # session.add(windows_build)

        session.commit()


def clear_database():
    clear_ecosystems()
    with session_scope() as session:
        session.query(Ecosystem).delete()


def clear_ecosystems():
    with session_scope() as session:
        session.query(Build).delete()
        session.query(Commit).delete()
        session.query(Channel).delete()
        session.query(Setting).delete()
        session.query(Profile).delete()
        session.query(Repo).delete()