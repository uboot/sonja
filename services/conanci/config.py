from conanci.database import Base, engine, logger
import connexion
import logging
import logging.config
import os
import sqlalchemy
import time
import yaml


app = connexion.App(__name__, specification_dir='./swagger/')


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
            Base.metadata.create_all(engine)
            logger.info("Connected to database")
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

