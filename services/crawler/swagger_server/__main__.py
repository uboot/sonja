#!/usr/bin/env python3

from conanci.config import app
from swagger_server import crawler
from swagger_server import encoder
import os.path
import signal

logger = app.app.logger
swagger_api = os.path.join(os.path.dirname(__file__), 'swagger', 'swagger.yaml')


def handler(signum, frame):
    logger.info("Signal handler called with signal SIGTERM")
    logger.info("Shutdown crawler")
    crawler.cancel()
    crawler.join()
    signal.signal(signal.SIGTERM, signal.SIG_DFL)
    signal.raise_signal(signum)


def main():
    signal.signal(signal.SIGTERM, handler)
    app.add_api(swagger_api, arguments={'title': 'Conan CI Crawler'}, pythonic_params=True)
    app.app.json_encoder = encoder.JSONEncoder
    crawler.start()
    app.run(port=8080)

if __name__ == '__main__':
    main()
