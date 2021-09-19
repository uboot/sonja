from sonja.database import Base, engine, insert_first_user, logger, session_scope
import connexion
import logging
import logging.config
import os
import sqlalchemy
import time
import yaml

from alembic import command
from alembic.config import Config
from alembic.runtime import migration


app = connexion.App(__name__, specification_dir='./swagger/')
initial_user = os.environ.get('SONJA_INITIAL_USER', 'user')
initial_password = os.environ.get('SONJA_INITIAL_PASSWORD', 'paSSwOrd')


class PingFilter(logging.Filter):
    def filter(self, record):
        return not "GET /ping" in record.msg


def setup_logging():
    with open(os.path.join(os.path.dirname(__file__), "logging.yaml")) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
    logging.config.dictConfig(config)


def connect_to_database():
    TIMEOUT = 10
    NUM_RETRIES = 18
    for i in range(1, NUM_RETRIES+1):
        logger.info("Connect to database, attempt %i of %i", i, NUM_RETRIES)
        try:
            alembic_cfg = Config()
            alembic_cfg.set_main_option("script_location", os.path.join(os.path.dirname(__file__), "alembic"))
            with session_scope() as session:
                context = migration.MigrationContext.configure(session.connection())
                revision = context.get_current_revision()
                alembic_cfg.attributes['connection'] = session.connection()
                if revision:
                    logger.info("Database is at revision %s", revision)
                    logger.info("Upgrade database")
                    command.upgrade(alembic_cfg, "head")
                else:
                    logger.info("Create new database")
                    Base.metadata.create_all(engine)
                    command.stamp(alembic_cfg, "head")
                new_revision = context.get_current_revision()
                logger.info("Database is at revision %s", new_revision)

                insert_first_user(initial_user, initial_password)
            logger.info("Connected")
            return
        except sqlalchemy.exc.OperationalError:
            logger.warning("Failed to connect to database")
            if i < NUM_RETRIES:
                logger.info("Try to reconnect in %i seconds", TIMEOUT)
                time.sleep(TIMEOUT)

    logger.error("Failed to connect to database after %i attempts", NUM_RETRIES)
    logger.error("Exit with 1")
    #os.kill(os.getpid(), signal.SIGKILL)
    exit(1)

