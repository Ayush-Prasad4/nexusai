from fastapi import FastAPI
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import get_settings


def add_trusted_host_middleware(app: FastAPI) -> None:
    settings = get_settings()

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts,
    )
