from fastapi import FastAPI
from public.api import router
from public.config import api_prefix

app = FastAPI(title="Public", openapi_url="/api/v1/openapi.json", docs_url="/api/v1/docs", redoc_url="/api/v1/redoc")

app.include_router(router, prefix=api_prefix)
