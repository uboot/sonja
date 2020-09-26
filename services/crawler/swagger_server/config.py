import connexion
from flask_sqlalchemy import SQLAlchemy
import logging
import os


app = connexion.App(__name__, specification_dir='./swagger/')
connection_string = 'mysql+mysqldb://root:{0}@{1}/conan-ci'.format(
    os.environ.get('MYSQL_ROOT_PASSWORD', ''),
    os.environ.get('MYSQL_URL', 'mysql')
)
app.app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
app.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app.app)
logging.basicConfig(level=logging.INFO)
