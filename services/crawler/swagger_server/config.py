import connexion
from flask_sqlalchemy import SQLAlchemy
import logging
import os

app = connexion.App(__name__, specification_dir='./swagger/')
app.app.config['SQLALCHEMY_DATABASE_URI'] = ('mysql+mysqldb://root:%s@127.0.0.1/conan-ci'
                                             % os.environ.get('MYSQL_ROOT_PASSWORD', ''))
app.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app.app)
logging.basicConfig(level=logging.INFO)