from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Table, Text, BigInteger
from sqlalchemy.dialects.mysql import LONGTEXT, TEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sonja.auth import hash_password

import enum

Base = declarative_base()


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
    ecosystem = relationship("Ecosystem", backref="git_credentials")


class DockerCredential(Base):
    __tablename__ = 'docker_credential'

    id = Column(Integer, primary_key=True)
    server = Column(String(255), nullable=False)
    username = Column(String(255))
    password = Column(String(255))
    ecosystem_id = Column(Integer, ForeignKey('ecosystem.id'))
    ecosystem = relationship("Ecosystem", backref="docker_credentials")


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
    def git_credential_values(self):
        return [{"url": c.url, "username": c.username, "password": c.password} for c in self.git_credentials]

    @git_credential_values.setter
    def git_credential_values(self, value):
        self.git_credentials = [GitCredential(**v) for v in value]

    @property
    def docker_credential_values(self):
        return [{"server": c.server, "username": c.username, "password": c.password} for c in self.docker_credentials]

    @docker_credential_values.setter
    def docker_credential_values(self, value):
        self.docker_credentials = [DockerCredential(**v) for v in value]


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


class Run(Base):
    __tablename__ = 'run'
    id = Column(Integer, primary_key=True)
    started = Column(DateTime, nullable=False, index=True)
    status = Column(Enum(BuildStatus), nullable=False)
    build_id = Column(Integer, ForeignKey('build.id'), index=True)
    build = relationship("Build", backref="runs")

    @property
    def status_value(self):
        return self.status.name

    @status_value.setter
    def status_value(self, value):
        self.status = BuildStatus[value.name]


missing_package = Table('missing_package', Base.metadata,
    Column('build_id', Integer, ForeignKey('build.id'), primary_key=True),
    Column('package_id', Integer, ForeignKey('package.id'), primary_key=True))


missing_recipe = Table('missing_recipe', Base.metadata,
    Column('build_id', Integer, ForeignKey('build.id'), primary_key=True),
    Column('recipe_id', Integer, ForeignKey('recipe.id'), primary_key=True))


class Build(Base):
    __tablename__ = 'build'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False, index=True)
    status = Column(Enum(BuildStatus), nullable=False)
    commit_id = Column(Integer, ForeignKey('commit.id'),
                          nullable=False)
    commit = relationship('Commit', backref='builds')
    package_id = Column(Integer, ForeignKey('package.id'))
    package = relationship("Package", backref="builds")
    profile_id = Column(Integer, ForeignKey('profile.id'), nullable=False)
    profile = relationship("Profile")
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


class LogLine(Base):
    __tablename__ = 'log_line'

    id = Column(BigInteger, primary_key=True)
    number = Column(Integer, nullable=False, index=True)
    time = Column(DateTime, nullable=False)
    content = Column(TEXT)
    run_id = Column(Integer, ForeignKey('run.id'), index=True)
    run = relationship("Run", backref="log_lines")


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
