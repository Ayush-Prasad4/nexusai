import asyncio
from uuid import uuid4

from redis.asyncio import Redis

from app.core.config import get_settings
from app.infrastructure.redis.rate_limiter import (
    RateLimitExceeded,
    RedisRateLimiter,
)


def test_rate_limiter_enforces_limit() -> None:
    async def scenario() -> None:
        redis = Redis.from_url(
            get_settings().redis_url,
            decode_responses=True,
        )

        key = f"nexusai:test:ratelimit:{uuid4()}"

        try:
            limiter = RedisRateLimiter(redis)

            assert await limiter.check(
                key=key,
                limit=2,
                window_seconds=60,
            ) == 1

            assert await limiter.check(
                key=key,
                limit=2,
                window_seconds=60,
            ) == 2

            try:
                await limiter.check(
                    key=key,
                    limit=2,
                    window_seconds=60,
                )
            except RateLimitExceeded:
                pass
            else:
                raise AssertionError(
                    "Expected rate limit to be exceeded."
                )

        finally:
            await redis.delete(key)
            await redis.aclose()

    asyncio.run(scenario())
