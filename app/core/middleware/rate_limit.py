from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import get_settings
from app.infrastructure.redis.rate_limiter import (
    RateLimitExceeded,
    RedisRateLimiter,
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        settings = get_settings()

        redis = getattr(request.app.state, "redis", None)

        if redis is None:
            return await call_next(request)

        limiter = RedisRateLimiter(redis)

        client_ip = request.client.host if request.client else "unknown"

        key = (
            f"nexusai:ratelimit:"
            f"ip:{client_ip}"
        )

        try:
            await limiter.check(
                key=key,
                limit=settings.rate_limit_requests,
                window_seconds=settings.rate_limit_window_seconds,
            )
        except RateLimitExceeded:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Rate limit exceeded.",
                },
                headers={
                    "Retry-After": str(
                        settings.rate_limit_window_seconds
                    ),
                },
            )

        return await call_next(request)
