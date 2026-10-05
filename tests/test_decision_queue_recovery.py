import asyncio
from uuid import uuid4

from redis.asyncio import Redis

from app.application.jobs.contracts import DecisionJob
from app.core.config import get_settings
from app.infrastructure.redis.queue import (
    DECISION_CONSUMER_GROUP,
    DECISION_STREAM,
    DecisionJobQueue,
)


def test_claimed_job_survives_worker_failure() -> None:
    async def scenario() -> None:
        redis = Redis.from_url(
            get_settings().redis_url,
            decode_responses=True,
        )

        try:
            await redis.delete(DECISION_STREAM)

            queue = DecisionJobQueue(
                redis,
                consumer_name=f"test-worker-{uuid4()}",
            )

            await queue.initialize()

            job = DecisionJob(
                job_id=uuid4(),
                decision_run_id=uuid4(),
            )

            stream_id = await queue.enqueue(job)

            processing_job = await queue.claim()

            assert processing_job is not None
            assert processing_job.job == job
            assert processing_job.stream_id == stream_id

            pending = await redis.xpending(
                DECISION_STREAM,
                DECISION_CONSUMER_GROUP,
            )

            assert pending["pending"] == 1

        finally:
            await redis.delete(DECISION_STREAM)
            await redis.delete(
                "nexusai:jobs:decision:dead-letter",
            )
            await redis.aclose()

    asyncio.run(scenario())
