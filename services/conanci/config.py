import connexion
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
import logging
import os
import signal


app = connexion.App(__name__, specification_dir='./swagger/')
connection_string = 'mysql+mysqldb://root:{0}@{1}/conan-ci'.format(
    os.environ.get('MYSQL_ROOT_PASSWORD', 'secret'),
    os.environ.get('MYSQL_URL', '127.0.0.1')
)
app.app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
app.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app.app)
logging.basicConfig(level=logging.INFO)
logger = app.app.logger

def connect_to_database():
    try:
        db.create_all()
    except sqlalchemy.exc.OperationalError:
        logger.warn("failed to connect to database")
        logger.warn("exit with 1")
        os.kill(os.getpid(), signal.SIGKILL)
        exit(1)
    