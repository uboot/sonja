#!/usr/bin/env python3
import uvicorn
from crawler.config import crawler
from crawler.main import app
from sonja.config import setup_logging, logger


@app.on_event("shutdown")
def shutdown_event():
    logger.info("Signal handler called with signal SIGTERM")
    logger.info("Shutdown crawler")
    crawler.cancel()
    crawler.join()


if __name__ == '__main__':
    setup_logging()
    crawler.start()
    uvicorn.run(app, host="0.0.0.0", port=8080)
