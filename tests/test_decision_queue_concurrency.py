

import asyncio
from uuid import uuid4

from redis.asyncio import Redis

from app.application.jobs.contracts import DecisionJob
from app.core.config import get_settings
from app.infrastructure.redis.queue import (
    DECISION_STREAM,
    DecisionJobQueue,
)


def test_multiple_workers_claim_distinct_jobs() -> None:
    async def scenario() -> None:
        redis = Redis.from_url(
            get_settings().redis_url,
            decode_responses=True,
        )

        try:
            await redis.delete(DECISION_STREAM)

            worker_a = DecisionJobQueue(
                redis,
                consumer_name=f"worker-a-{uuid4()}",
            )

            worker_b = DecisionJobQueue(
                redis,
                consumer_name=f"worker-b-{uuid4()}",
            )

            await worker_a.initialize()
            await worker_b.initialize()

            job_a = DecisionJob(
                job_id=uuid4(),
                decision_run_id=uuid4(),
            )

            job_b = DecisionJob(
                job_id=uuid4(),
                decision_run_id=uuid4(),
            )

            await worker_a.enqueue(job_a)
            await worker_a.enqueue(job_b)

            claimed_a, claimed_b = await asyncio.gather(
                worker_a.claim(),
                worker_b.claim(),
            )

            assert claimed_a is not None
            assert claimed_b is not None

            claimed_ids = {
                claimed_a.job.job_id,
                claimed_b.job.job_id,
            }

            assert claimed_ids == {
                job_a.job_id,
                job_b.job_id,
            }

            assert (
                claimed_a.job.job_id
                != claimed_b.job.job_id
            )

        finally:
            await redis.delete(DECISION_STREAM)
            await redis.aclose()

    asyncio.run(scenario())
