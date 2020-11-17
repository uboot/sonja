from conanci.database import Base, engine
import connexion
import logging
import os
import signal
import sqlalchemy


app = connexion.App(__name__, specification_dir='./swagger/')
logging.basicConfig(level=logging.INFO)
logger = app.app.logger


def connect_to_database():
    try:
        Base.metadata.create_all(engine)
    except sqlalchemy.exc.OperationalError:
        logger.warning("failed to connect to database")
        logger.warning("exit with 1")
        os.kill(os.getpid(), signal.SIGKILL)
        exit(1)