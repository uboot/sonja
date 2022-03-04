from fastapi import FastAPI
from agent.api import router

app = FastAPI(title="Agent")

app.include_router(router)
