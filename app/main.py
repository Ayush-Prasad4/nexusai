from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.core.errors.exceptions import NexusAIException
from app.core.errors.handlers import nexusai_exception_handler
from app.core.middleware.request_id import RequestIDMiddleware
from app.observability.logging import configure_logging
from app.infrastructure.redis.client import redis_client


configure_logging()

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await redis_client.ping()
    yield
    await redis_client.aclose()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_exception_handler(
    NexusAIException,
    nexusai_exception_handler,
)

app.add_middleware(RequestIDMiddleware)

app.include_router(api_router)
