from sqlalchemy import create_engine, exists, literal, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from sonja.auth import hash_password
from sonja.model import User, Permission, PermissionLabel, Ecosystem, Base, Build, missing_package, missing_recipe, \
    package_requirement, Package, RecipeRevision, Recipe, Commit, Channel, DockerCredential, GitCredential, \
    profile_label, Profile, Label, Repo, Option, repo_label, Run, LogLine, Configuration, ConanCredential
from sonja.ssh import encode, generate_rsa_key

from contextlib import contextmanager
from secrets import token_hex
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


def create_initial_user(name: str, password: str):
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


def create_initial_configuration():
    secret = token_hex(20)
    with session_scope() as session:
        statement = \
            Configuration.__table__.insert(). \
            from_select([Configuration.github_secret],
                        select([literal(secret)]).
                        where(~exists().where(Configuration.id)))
        result = session.execute(statement)

        if result.lastrowid:
            configuration = session.query(Configuration).filter_by(id=result.lastrowid).first()
            private, public = generate_rsa_key()
            configuration.ssh_key = encode(private)
            configuration.public_ssh_key = encode(public)
            logger.info("Created initial configuration with ID %d", configuration.id)


def create_initial_ecosystem(name: str) -> int:
    with session_scope() as session:
        statement = \
            Ecosystem.__table__.insert(). \
            from_select([Ecosystem.name],
                        select([literal(name)]).
                        where(~exists().where(Ecosystem.id)))
        result = session.execute(statement)

        if result.lastrowid:
            ecosystem = session.query(Ecosystem).filter_by(id=result.lastrowid).first()
            logger.info("Created initial ecosystem with ID %d", ecosystem.id)
            return ecosystem.id

        return 0


def get_current_configuration(session: Session) -> Configuration:
    return session.query(Configuration).first()


def remove_but_last_user(session: Session, user_id: str):
    record = session.query(User).filter_by(id=user_id).first()
    if not record:
        raise NotFound
    session.delete(record)
    if session.query(User).count() == 0:
        session.rollback()
        raise OperationFailed


def reset_database():
    clear_database()


def _activate_foreign_key_check():
    with session_scope() as session:
        session.execute("SET FOREIGN_KEY_CHECKS=0")


def _deactivate_foreign_key_check():
    with session_scope() as session:
        session.execute("SET FOREIGN_KEY_CHECKS=1")


def _drop_table(table):
    try:
        table.drop(engine)
    except OperationalError as e:
        logger.warning("Failed to drop table %s", table.name)
            
            
def _drop_data_tables():
    _activate_foreign_key_check()
    _drop_table(missing_package)
    _drop_table(missing_recipe)
    _drop_table(LogLine.__table__)
    _drop_table(Run.__table__)
    _drop_table(Build.__table__)
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
    _activate_foreign_key_check()
    
            
def clear_database():
    _drop_data_tables()

    _drop_table(GitCredential.__table__)
    _drop_table(DockerCredential.__table__)
    _drop_table(ConanCredential.__table__)
    _drop_table(Ecosystem.__table__)
    _drop_table(Permission.__table__)
    _drop_table(User.__table__)
    _drop_table(Configuration.__table__)

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
