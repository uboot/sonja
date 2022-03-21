from sqlalchemy import create_engine, Column, Enum, exists, ForeignKey, Integer, literal, select, String,\
    Table, Text
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sonja.auth import hash_password

from contextlib import contextmanager
import enum
import logging
import os

# start MySQL:
# docker run --rm -d --name mysql -p 3306:3306 -e MYSQL_DATABASE=sonja -e MYSQL_ROOT_PASSWORD=secret mysql:8.0.21
# docker run --rm -d --name phpmyadmin --link mysql:db -p 8081:80 phpmyadmin:5.0.4

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sonja")


class ErrorCodes(object):
    DUPLICATE_ENTRY = 1062


connection_string = 'mysql+mysqldb://root:{0}@{1}/sonja'.format(
    os.environ.get('MYSQL_ROOT_PASSWORD', 'secret'),
    os.environ.get('MYSQL_URL', '127.0.0.1')
)
Base = declarative_base()
engine = create_engine(connection_string, echo=False)
Session = sessionmaker(engine)


class NotFound(Exception):
    pass


class OperationFailed(Exception):
    pass


def get_session():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    return get_session()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    user_name = Column(String(255), nullable=False, unique=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    password = Column(String(255))
    email = Column(String(255))

    @property
    def permission_value(self):
        return [{"permission": p.label.name} for p in self.permissions]

    @permission_value.setter
    def permission_value(self, value):
        self.permissions = [Permission(label=PermissionLabel[v["permission"]]) for v in value]

    @property
    def plain_password(self):
        return ""

    @plain_password.setter
    def plain_password(self, value):
        self.password = hash_password(value)


class PermissionLabel(enum.Enum):
    read = 1
    write = 2
    admin = 3


class Permission(Base):
    __tablename__ = 'permission'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", backref="permissions")
    label = Column(Enum(PermissionLabel), nullable=False)


class GitCredential(Base):
    __tablename__ = 'git_credential'

    id = Column(Integer, primary_key=True)
    url = Column(String(255), nullable=False)
    username = Column(String(255))
    password = Column(String(255))
    ecosystem_id = Column(Integer, ForeignKey('ecosystem.id'))
    ecosystem = relationship("Ecosystem", backref="credentials")


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

    @property
    def credential_values(self):
        return [{"url": c.url, "username": c.username, "password": c.password} for c in self.credentials]

    @credential_values.setter
    def credential_values(self, value):
        self.credentials = [GitCredential(**v) for v in value]


class Label(Base):
    __tablename__ = 'label'

    id = Column(Integer, primary_key=True)
    value = Column(String(255), nullable=False)


repo_label = Table('repo_label', Base.metadata,
                   Column('repo_id', Integer, ForeignKey('repo.id')),
                   Column('label_id', Integer, ForeignKey('label.id')))


class Option(Base):
    __tablename__ = 'option'

    id = Column(Integer, primary_key=True)
    key = Column(String(255), nullable=False)
    value = Column(String(255), nullable=False)
    repo_id = Column(Integer, ForeignKey('repo.id'), nullable=False)


class Repo(Base):
    __tablename__ = 'repo'

    id = Column(Integer, primary_key=True)
    ecosystem_id = Column(Integer, ForeignKey('ecosystem.id'))
    ecosystem = relationship("Ecosystem", backref="repos")
    name = Column(String(255))
    url = Column(String(255))
    path = Column(String(255))
    version = Column(String(255))
    exclude = relationship("Label", secondary=repo_label)
    options = relationship('Option', backref='repo', lazy=True,
                            cascade="all, delete, delete-orphan")

    @property
    def exclude_values(self):
        return [{"label": e.value} for e in self.exclude]

    @exclude_values.setter
    def exclude_values(self, value):
        self.exclude = [Label(value=v["label"]) for v in value]

    @property
    def options_values(self):
        return [{"key": o.key, "value": o.value} for o in self.options]

    @options_values.setter
    def options_values(self, value):
        self.options = [Option(**v) for v in value]


class Channel(Base):
    __tablename__ = 'channel'

    id = Column(Integer, primary_key=True)
    ecosystem_id = Column(Integer, ForeignKey('ecosystem.id'))
    ecosystem = relationship("Ecosystem", backref="channels")
    name = Column(String(255), nullable=False)
    conan_channel = Column(String(255))
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

    @property
    def platform_value(self):
        return self.platform.name

    @platform_value.setter
    def platform_value(self, value):
        self.platform = Platform[value.name]

    @property
    def labels_value(self):
        return [{"label": l.value} for l in self.labels]

    @labels_value.setter
    def labels_value(self, value):
        self.labels = [Label(value=v["label"]) for v in value]


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


missing_package = Table('missing_package', Base.metadata,
    Column('build_id', Integer, ForeignKey('build.id'), primary_key=True),
    Column('package_id', Integer, ForeignKey('package.id'), primary_key=True))


missing_recipe = Table('missing_recipe', Base.metadata,
    Column('build_id', Integer, ForeignKey('build.id'), primary_key=True),
    Column('recipe_id', Integer, ForeignKey('recipe.id'), primary_key=True))


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
    missing_packages = relationship("Package", secondary=missing_package)
    missing_recipes = relationship("Recipe", secondary=missing_recipe)

    @property
    def ecosystem(self):
        return self.profile.ecosystem

    @property
    def status_value(self):
        return self.status.name

    @status_value.setter
    def status_value(self, value):
        self.status = BuildStatus[value.name]


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


def insert_first_user(name: str, password: str):
    if not name or not password:
        logger.warning("No initial user/password provided")
        return

    with session_scope() as session:
        password_hash = hash_password(password)
        statement = \
            User.__table__.insert(). \
            from_select([User.user_name, User.password],
                        select([literal(name), literal(password_hash)]).
                        where(~exists().where(User.id)))
        result = session.execute(statement)

        if result.lastrowid:
            user = session.query(User).filter_by(id=result.lastrowid).first()
            user.permissions = [
                Permission(label=PermissionLabel.read),
                Permission(label=PermissionLabel.write),
                Permission(label=PermissionLabel.admin)
            ]
            logger.info("Created initial user with ID %d", user.id)


def remove_but_last_user(session: Session, user_id: str):
    record = session.query(User).filter_by(id=user_id).first()
    if not record:
        raise NotFound
    session.delete(record)
    if session.query(User).count() == 0:
        session.rollback()
        raise OperationFailed


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
        hello.url = "git@github.com:uboot/sonja-backend.git"
        hello.path = "packages/hello"
        hello.exclude = [
            Label(value="debug")
        ]
        hello.options = [
             Option(key="hello:shared", value="False")
        ]
        session.add(hello)

        base = Repo()
        base.name = "Base"
        base.ecosystem = ecosystem
        base.url = "git@github.com:uboot/sonja-backend.git"
        base.path = "packages/base"
        base.exclude = [
            Label(value="debug")
        ]
        session.add(hello)

        app = Repo()
        app.name = "App"
        app.ecosystem = ecosystem
        app.url = "git@github.com:uboot/sonja-backend.git"
        app.path = "packages/app"
        app.exclude = [
            Label(value="debug")
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
            Label(value="debug")
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
            Label(value="debug")
        ]
        session.add(windows_debug)

        channel = Channel()
        channel.ecosystem = ecosystem
        channel.name = "Releases"
        channel.branch = "master"
        channel.conan_channel = "stable"
        session.add(channel)

        session.commit()


def _drop_table(table):
    try:
        table.drop(engine)
    except OperationalError as e:
        logger.warning("Failed to drop table %s", table.name)
            
            
def _drop_data_tables():
    _drop_table(missing_package)
    _drop_table(missing_recipe)
    _drop_table(Build.__table__)
    _drop_table(Log.__table__)
    _drop_table(package_requirement)
    _drop_table(Package.__table__)
    _drop_table(RecipeRevision.__table__)
    _drop_table(Recipe.__table__)
    _drop_table(Commit.__table__)
    _drop_table(Channel.__table__)
    _drop_table(profile_label)
    _drop_table(Profile.__table__)
    _drop_table(repo_label)
    _drop_table(Label.__table__)
    _drop_table(Option.__table__)
    _drop_table(Repo.__table__)
    
            
def clear_database():
    _drop_data_tables()

    _drop_table(GitCredential.__table__)
    _drop_table(Ecosystem.__table__)
    _drop_table(Permission.__table__)
    _drop_table(User.__table__)

    try:
        Base.metadata.create_all(engine)
    except OperationalError:
        logger.warning("Failed to connect to database")
        raise


def clear_ecosystems():
    _drop_data_tables()

    try:
        Base.metadata.create_all(engine)
    except OperationalError:
        logger.warning("Failed to connect to database")
        raise
