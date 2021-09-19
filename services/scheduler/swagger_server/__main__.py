#!/usr/bin/env python3

from sonja.config import app, setup_logging
from swagger_server import scheduler
from swagger_server import encoder
import os.path
import signal

logger = app.app.logger
swagger_api = os.path.join(os.path.dirname(__file__), 'swagger', 'swagger.yaml')


def handler(signum, frame):
    logger.info("Signal handler called with signal SIGTERM")
    logger.info("Shutdown scheduler")
    scheduler.cancel()
    scheduler.join()
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    signal.raise_signal(signum)


def main():
    signal.signal(signal.SIGTERM, handler)
    app.add_api(swagger_api, arguments={'title': 'Linux Scheduler'}, pythonic_params=True)
    app.app.json_encoder = encoder.JSONEncoder
    setup_logging()
    scheduler.start()
    app.run(port=8080)

if __name__ == '__main__':
    main()
