import asyncio

import pytest

from app.application.reliability.executor import execute_with_retry
from app.application.reliability.retry import RetryPolicy


def test_execute_with_retry_succeeds_after_transient_failures() -> None:
    attempts = 0
    delays: list[float] = []

    async def operation() -> str:
        nonlocal attempts

        attempts += 1

        if attempts < 3:
            raise RuntimeError("temporary failure")

        return "success"

    async def fake_sleep(delay: float) -> None:
        delays.append(delay)

    result = asyncio.run(
        execute_with_retry(
            operation,
            RetryPolicy(
                max_attempts=3,
                base_delay_seconds=1.0,
            ),
            sleep=fake_sleep,
        )
    )

    assert result == "success"
    assert attempts == 3
    assert delays == [1.0, 2.0]


def test_execute_with_retry_raises_after_max_attempts() -> None:
    attempts = 0
    delays: list[float] = []

    async def operation() -> str:
        nonlocal attempts

        attempts += 1
        raise RuntimeError("permanent failure")

    async def fake_sleep(delay: float) -> None:
        delays.append(delay)

    with pytest.raises(RuntimeError, match="permanent failure"):
        asyncio.run(
            execute_with_retry(
                operation,
                RetryPolicy(
                    max_attempts=3,
                    base_delay_seconds=1.0,
                ),
                sleep=fake_sleep,
            )
        )

    assert attempts == 3
    assert delays == [1.0, 2.0]
