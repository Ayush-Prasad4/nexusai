import asyncio
from uuid import uuid4

from redis.asyncio import Redis

from app.application.jobs.contracts import DecisionJob
from app.application.jobs.dead_letter import DeadLetterJob
from app.core.config import get_settings
from app.infrastructure.redis.queue import (
    DECISION_CONSUMER_GROUP,
    DECISION_DLQ,
    DECISION_STREAM,
    DecisionJobQueue,
)


def test_stale_job_is_recovered_until_max_attempts() -> None:
    async def scenario() -> None:
        redis = Redis.from_url(
            get_settings().redis_url,
            decode_responses=True,
        )

        try:
            await redis.delete(
                DECISION_STREAM,
                DECISION_DLQ,
            )

            queue = DecisionJobQueue(
                redis,
                consumer_name=f"test-worker-{uuid4()}",
            )

            await queue.initialize()

            job = DecisionJob(
                job_id=uuid4(),
                decision_run_id=uuid4(),
            )

            await queue.enqueue(job)

            processing_job = await queue.claim()

            assert processing_job is not None
            assert processing_job.attempt == 1

            recovered, dead_lettered = (
                await queue.recover_stale_jobs(
                    lease_seconds=0,
                    max_attempts=3,
                )
            )

            assert recovered == 1
            assert dead_lettered == 0

            retry_job = await queue.claim()

            assert retry_job is not None
            assert retry_job.attempt == 2
            assert retry_job.job.job_id == job.job_id

        finally:
            await redis.delete(
                DECISION_STREAM,
                DECISION_DLQ,
            )
            await redis.aclose()

    asyncio.run(scenario())


def test_max_attempts_moves_job_to_dlq() -> None:
    async def scenario() -> None:
        redis = Redis.from_url(
            get_settings().redis_url,
            decode_responses=True,
        )

        try:
            await redis.delete(
                DECISION_STREAM,
                DECISION_DLQ,
            )

            queue = DecisionJobQueue(
                redis,
                consumer_name=f"test-worker-{uuid4()}",
            )

            await queue.initialize()

            job = DecisionJob(
                job_id=uuid4(),
                decision_run_id=uuid4(),
                attempt=3,
            )

            await queue.enqueue(job)

            processing_job = await queue.claim()

            assert processing_job is not None
            assert processing_job.attempt == 3

            recovered, dead_lettered = (
                await queue.recover_stale_jobs(
                    lease_seconds=0,
                    max_attempts=3,
                )
            )

            assert recovered == 0
            assert dead_lettered == 1

            payload = await redis.lpop(
                DECISION_DLQ,
            )

            assert payload is not None

            dead_letter = DeadLetterJob.model_validate_json(
                payload,
            )

            assert dead_letter.job.job_id == job.job_id
            assert dead_letter.job.decision_run_id == job.decision_run_id
            assert dead_letter.job.attempt == 3
            assert dead_letter.attempts == 3
            assert dead_letter.reason == (
                "maximum delivery attempts exceeded"
            )

            pending = await redis.xpending(
                DECISION_STREAM,
                DECISION_CONSUMER_GROUP,
            )

            assert pending["pending"] == 0

        finally:
            await redis.delete(
                DECISION_STREAM,
                DECISION_DLQ,
            )
            await redis.aclose()

    asyncio.run(scenario())
