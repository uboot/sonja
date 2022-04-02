#!/usr/bin/env python3

import uvicorn
from public.main import app
from sonja.config import connect_to_database, log_config, setup_initial_data


if __name__ == '__main__':
    connect_to_database()
    setup_initial_data()
    uvicorn.run(app, host="0.0.0.0", port=8080, log_config=log_config)
