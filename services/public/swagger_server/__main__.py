#!/usr/bin/env python3

import connexion
from flask_sqlalchemy import SQLAlchemy
from swagger_server import encoder

app = connexion.App(__name__, specification_dir='./swagger/')
app.app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:secret@127.0.0.1/conan-ci'
app.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app.app)

class Repo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)

    def __init__(self, url=None):
        self.url = url

    def __repr__(self):
        return "Repo(%r)" % (self.url)

def main():
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('swagger.yaml', arguments={'title': 'Conan-CI Public API'}, pythonic_params=True)
    db.create_all()
    app.run(port=8080)


if __name__ == '__main__':
    main()
