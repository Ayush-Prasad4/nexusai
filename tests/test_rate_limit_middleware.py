from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.middleware.rate_limit import RateLimitMiddleware
from app.infrastructure.redis.rate_limiter import (
    RateLimitExceeded,
)


@pytest.fixture
def rate_limited_app() -> FastAPI:
    app = FastAPI()

    redis = AsyncMock()
    app.state.redis = redis

    app.add_middleware(RateLimitMiddleware)

    @app.get("/test")
    async def test_endpoint():
        return {"ok": True}

    return app


def test_rate_limit_middleware_allows_request(
    rate_limited_app: FastAPI,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def allow_request(
        self,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> int:
        return 1

    monkeypatch.setattr(
        "app.infrastructure.redis.rate_limiter.RedisRateLimiter.check",
        allow_request,
    )

    with TestClient(rate_limited_app) as client:
        response = client.get("/test")

    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_rate_limit_middleware_returns_429(
    rate_limited_app: FastAPI,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def reject_request(
        self,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> int:
        raise RateLimitExceeded

    monkeypatch.setattr(
        "app.infrastructure.redis.rate_limiter.RedisRateLimiter.check",
        reject_request,
    )

    with TestClient(rate_limited_app) as client:
        response = client.get("/test")

    assert response.status_code == 429
    assert response.json()["detail"] == "Rate limit exceeded."
    assert response.headers["Retry-After"] == "60"
