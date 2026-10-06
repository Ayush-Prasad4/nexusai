from redis.asyncio import Redis


class RateLimitExceeded(Exception):
    """Raised when a rate limit is exceeded."""


class RedisRateLimiter:
    def __init__(
        self,
        redis: Redis,
    ) -> None:
        self.redis = redis

    async def check(
        self,
        key: str,
        limit: int,
        window_seconds: int,
    ) -> int:
        if limit <= 0:
            raise ValueError("Rate limit must be greater than zero.")

        if window_seconds <= 0:
            raise ValueError(
                "Rate-limit window must be greater than zero."
            )

        count = await self.redis.incr(key)

        if count == 1:
            await self.redis.expire(
                key,
                window_seconds,
            )

        if count > limit:
            raise RateLimitExceeded

        return count
