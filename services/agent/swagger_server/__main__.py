#!/usr/bin/env python3

from conanci.config import app, connect_to_database
from swagger_server import agent
from swagger_server import encoder
import os.path
import signal

logger = app.app.logger
swagger_api = os.path.join(os.path.dirname(__file__), 'swagger', 'swagger.yaml')


def handler(signum, frame):
    logger.info("Signal handler called with signal SIGTERM")
    logger.info("Shutdown agent")
    agent.shutdown()
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    signal.raise_signal(signum)


def main():
    signal.signal(signal.SIGTERM, handler)
    app.add_api(swagger_api, arguments={'title': 'Conan CI Linux Agent'}, pythonic_params=True)
    app.app.json_encoder = encoder.JSONEncoder
    agent.start()
    app.run(port=8080)

if __name__ == '__main__':
    main()
