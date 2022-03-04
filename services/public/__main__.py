#!/usr/bin/env python3

import uvicorn
from public.main import app
from sonja.config import connect_to_database, setup_logging


if __name__ == '__main__':
    setup_logging()
    connect_to_database()
    uvicorn.run(app, host="0.0.0.0", port=8080)
