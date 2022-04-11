from fastapi import FastAPI
from fastapi_plugins import redis_plugin
from public.api import router
from public.config import api_prefix

app = FastAPI(title="Public", openapi_url="/api/v1/openapi.json", docs_url="/api/v1/docs", redoc_url="/api/v1/redoc")


@app.on_event("startup")
async def on_startup() -> None:
    await redis_plugin.init_app(app)
    await redis_plugin.init()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await redis_plugin.terminate()


app.include_router(router, prefix=api_prefix)
