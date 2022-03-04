from fastapi import FastAPI
from crawler.api import router

app = FastAPI(title="Crawler")

app.include_router(router)
