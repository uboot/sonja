from sqlalchemy import Boolean, create_engine, Column, Enum, ForeignKey, Integer, String, Table, Text
from sqlalchemy.dialects.mysql import LONGTEXT
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


class Ecosystem(Base):
    __tablename__ = 'ecosystem'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    user = Column(String(255))
    public_ssh_key = Column(Text())
    ssh_key = Column(Text())
    known_hosts = Column(Text())
    conan_config_url = Column(String(255))
    conan_config_path = Column(String(255))
    conan_config_branch = Column(String(255))
    conan_remote = Column(String(255))
    conan_user = Column(String(255))
    conan_password = Column(String(255))


class Label(Base):
    __tablename__ = 'label'

    id = Column(Integer, primary_key=True)
    value = Column(String(255), nullable=False)

    def __init__(self, value):
        self.value = value


repo_label = Table('repo_label', Base.metadata,
                   Column('repo_id', Integer, ForeignKey('repo.id')),
                   Column('label_id', Integer, ForeignKey('label.id')))


class Repo(Base):
    __tablename__ = 'repo'

    id = Column(Integer, primary_key=True)
    ecosystem_id = Column(Integer, ForeignKey('ecosystem.id'))
    ecosystem = relationship("Ecosystem", backref="repos")
    name = Column(String(255))
    url = Column(String(255))
    path = Column(String(255))
    exclude = relationship("Label", secondary=repo_label)


class Channel(Base):
    __tablename__ = 'channel'

    id = Column(Integer, primary_key=True)
    ecosystem_id = Column(Integer, ForeignKey('ecosystem.id'))
    ecosystem = relationship("Ecosystem", backref="channels")
    name = Column(String(255), nullable=False)
    branch = Column(String(255))


class Platform(enum.Enum):
    linux = 1
    windows = 2


profile_label = Table('profile_label', Base.metadata,
    Column('profile_id', Integer, ForeignKey('profile.id')),
    Column('label_id', Integer, ForeignKey('label.id')))


class Profile(Base):
    __tablename__ = 'profile'

    id = Column(Integer, primary_key=True)
    ecosystem_id = Column(Integer, ForeignKey('ecosystem.id'))
    ecosystem = relationship("Ecosystem", backref="profiles")
    name = Column(String(255), nullable=False)
    platform = Column(Enum(Platform))
    conan_profile = Column(String(255))
    container = Column(String(255))
    docker_user = Column(String(255))
    docker_password = Column(String(255))
    labels = relationship("Label", secondary=profile_label)


class CommitStatus(enum.Enum):
    new = 1
    building = 2
    old = 3


class Commit(Base):
    __tablename__ = 'commit'

    id = Column(Integer, primary_key=True)
    status = Column(Enum(CommitStatus), nullable=False)
    sha = Column(String(255), nullable=False)
    message = Column(String(255))
    user_name = Column(String(255))
    user_email = Column(String(255))
    repo_id = Column(Integer, ForeignKey('repo.id'), nullable=False)
    repo = relationship('Repo', backref='commits')
    channel_id = Column(Integer, ForeignKey('channel.id'), nullable=False)
    channel = relationship('Channel', backref='commits')


class BuildStatus(enum.Enum):
    new = 1
    active = 2
    error = 3
    success = 4
    stopping = 5
    stopped = 6


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
    log_id = Column(Integer, ForeignKey('log.id'), nullable=False)
    log = relationship("Log")


class Log(Base):
    __tablename__ = 'log'

    id = Column(Integer, primary_key=True)
    logs = Column(LONGTEXT, nullable=False)


class Recipe(Base):
    __tablename__ = 'recipe'

    id = Column(Integer, primary_key=True)
    ecosystem_id = Column(Integer, ForeignKey('ecosystem.id'))
    ecosystem = relationship("Ecosystem", backref="recipes")
    name = Column(String(255), nullable=False)
    version = Column(String(255))
    user = Column(String(255))
    channel = Column(String(255))
    revision = Column(String(255))


class RecipeRevision(Base):
    __tablename__ = 'recipe_revision'

    id = Column(Integer, primary_key=True)
    recipe_id = Column(Integer, ForeignKey('recipe.id'))
    recipe = relationship("Recipe", backref="revisions")
    revision = Column(String(255))


package_requirement = Table('package_requirement', Base.metadata,
    Column('package_id', Integer, ForeignKey('package.id'), primary_key=True),
    Column('requirement_id', Integer, ForeignKey('package.id'), primary_key=True))


class Package(Base):
    __tablename__ = 'package'

    id = Column(Integer, primary_key=True)
    package_id = Column(String(255), nullable=False)
    recipe_revision_id = Column(Integer, ForeignKey('recipe_revision.id'),
                         nullable=False)
    recipe_revision = relationship('RecipeRevision', backref='packages')
    requires = relationship('Package', secondary=package_requirement,
                            primaryjoin=package_requirement.c.package_id == id,
                            secondaryjoin=package_requirement.c.requirement_id == id,
                            backref='required_by')


def reset_database():
        try:
            Base.metadata.drop_all(engine)
            Base.metadata.create_all(engine)
        except OperationalError:
            logger.warning("Failed to connect to database")
            raise


def populate_database():
    logger.info("Populate database")
    with session_scope() as session:
        ecosystem = session.query(Ecosystem).filter_by(id=1).first()
        if not ecosystem:
            raise Exception("Found no ecosystem with ID=1")

        hello = Repo()
        hello.name = "Hello"
        hello.ecosystem = ecosystem
        hello.url = "git@github.com:uboot/conan-ci.git"
        hello.path = "packages/hello"
        hello.exclude = [
            Label("debug")
        ]
        session.add(hello)

        base = Repo()
        base.name = "Base"
        base.ecosystem = ecosystem
        base.url = "git@github.com:uboot/conan-ci.git"
        base.path = "packages/base"
        base.exclude = [
            Label("debug")
        ]
        session.add(hello)

        app = Repo()
        app.name = "App"
        app.ecosystem = ecosystem
        app.url = "git@github.com:uboot/conan-ci.git"
        app.path = "packages/app"
        app.exclude = [
            Label("debug")
        ]
        session.add(hello)

        linux_release = Profile()
        linux_release.ecosystem = ecosystem
        linux_release.platform = Platform.linux
        linux_release.name = "GCC 9 Release"
        linux_release.container = "uboot/gcc9:latest"
        linux_release.conan_profile = "linux-release"
        session.add(linux_release)

        linux_debug = Profile()
        linux_debug.ecosystem = ecosystem
        linux_debug.platform = Platform.linux
        linux_debug.name = "GCC 9 Debug"
        linux_debug.container = "uboot/gcc9:latest"
        linux_debug.conan_profile = "linux-debug"
        linux_debug.labels = [
            Label("debug")
        ]
        session.add(linux_debug)

        windows_release = Profile()
        windows_release.ecosystem = ecosystem
        windows_release.platform = Platform.windows
        windows_release.name = "MSVC 15 Release"
        windows_release.container = "uboot/msvc15:latest"
        windows_release.conan_profile = "windows-release"
        session.add(windows_release)

        windows_debug = Profile()
        windows_debug.ecosystem = ecosystem
        windows_debug.platform = Platform.windows
        windows_debug.name = "MSVC 15 Debug"
        windows_debug.container = "uboot/msvc15:latest"
        windows_debug.conan_profile = "windows-debug"
        windows_debug.labels = [
            Label("debug")
        ]
        session.add(windows_debug)

        channel = Channel()
        channel.ecosystem = ecosystem
        channel.branch = "master"
        channel.name = "stable"
        session.add(channel)

        session.commit()


def clear_database():
    reset_database()


def clear_ecosystems():
    def drop_table(table):
        try:
            table.drop(engine)
        except OperationalError as e:
            logger.warning("Failed to drop table %s", table.name)

    drop_table(Build.__table__)
    drop_table(Log.__table__)
    drop_table(package_requirement)
    drop_table(Package.__table__)
    drop_table(RecipeRevision.__table__)
    drop_table(Recipe.__table__)
    drop_table(Commit.__table__)
    drop_table(Channel.__table__)
    drop_table(profile_label)
    drop_table(Profile.__table__)
    drop_table(repo_label)
    drop_table(Repo.__table__)
    drop_table(Label.__table__)

    try:
        Base.metadata.create_all(engine)
    except OperationalError:
        logger.warning("Failed to connect to database")
        raise