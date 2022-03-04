from fastapi import FastAPI
from scheduler.api import router

app = FastAPI(title="Scheduler")

app.include_router(router)
