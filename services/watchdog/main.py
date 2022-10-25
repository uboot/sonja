from fastapi import FastAPI
from watchdog.api import router

app = FastAPI(title="Watchdog")

app.include_router(router)
