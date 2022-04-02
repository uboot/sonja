#!/usr/bin/env python3
import uvicorn
from scheduler.config import scheduler
from scheduler.main import app
from sonja.config import setup_logging, logger, log_config


@app.on_event("shutdown")
def shutdown_event():
    logger.info("Signal handler called with signal SIGTERM")
    logger.info("Shutdown scheduler")
    scheduler.cancel()
    scheduler.join()


if __name__ == '__main__':
    setup_logging()
    scheduler.start()
    uvicorn.run(app, host="0.0.0.0", port=8080, log_config=log_config)
