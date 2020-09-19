#!/usr/bin/env python3

from swagger_server.config import app, db
from swagger_server import encoder

def main():
    app.add_api('swagger.yaml', arguments={'title': 'Conan CI Crawler'}, pythonic_params=True)
    app.app.json_encoder = encoder.JSONEncoder
    db.create_all()
    app.run(port=8081)

if __name__ == '__main__':
    main()
