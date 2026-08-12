import logging

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging_config import configure_logging
from app.db.init_db import initialize_database

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from app.core.rate_limit import limiter

from app.core.middleware import (
    request_monitoring_middleware,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    settings.create_storage_directories()
    initialize_database()

    logger.info("Starting %s", settings.app_name)

    yield

    logger.info("Shutting down %s", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="GenAI customer support bot for the application",
    lifespan=lifespan,
)

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)

app.add_middleware(SlowAPIMiddleware)

app.middleware("http")(request_monitoring_middleware)

app.mount(
    "/static",
    StaticFiles(directory="app/web/static"),
    name="static",
)


@app.get(
    "/",
    include_in_schema=False,
)
def chat_page():
    return FileResponse("app/web/index.html")


app.include_router(
    api_router,
    prefix=settings.api_prefix,
)


@app.get(
    "/admin",
    include_in_schema=False,
)
def admin_page():
    return FileResponse("app/web/admin.html")


register_exception_handlers(app)
