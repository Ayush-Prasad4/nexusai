import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

from app.application.reliability.retry import RetryPolicy


T = TypeVar("T")


async def execute_with_retry(
    operation: Callable[[], Awaitable[T]],
    policy: RetryPolicy,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> T:
    attempt = 1

    while True:
        try:
            return await operation()
        except Exception:
            if not policy.can_retry(attempt):
                raise

            await sleep(policy.delay_seconds(attempt))
            attempt += 1
