from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.core.errors.exceptions import NexusAIException
from app.core.errors.handlers import nexusai_exception_handler


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)

app.add_exception_handler(
    NexusAIException,
    nexusai_exception_handler,
)

app.include_router(api_router)
