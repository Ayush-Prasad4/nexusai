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


def test_heartbeat_refreshes_pending_job_idle_time() -> None:
    async def scenario() -> None:
        redis = Redis.from_url(
            get_settings().redis_url,
            decode_responses=True,
        )

        try:
            await redis.delete(DECISION_STREAM)

            queue = DecisionJobQueue(
                redis,
                consumer_name=f"heartbeat-worker-{uuid4()}",
            )

            await queue.initialize()

            job = DecisionJob(
                job_id=uuid4(),
                decision_run_id=uuid4(),
            )

            await queue.enqueue(job)

            processing_job = await queue.claim()

            assert processing_job is not None
            assert processing_job.stream_id is not None

            await asyncio.sleep(0.05)

            before = await redis.xpending_range(
                DECISION_STREAM,
                DECISION_CONSUMER_GROUP,
                min="-",
                max="+",
                count=10,
            )

            assert len(before) == 1

            idle_before = before[0]["time_since_delivered"]

            await queue.heartbeat(processing_job)

            after = await redis.xpending_range(
                DECISION_STREAM,
                DECISION_CONSUMER_GROUP,
                min="-",
                max="+",
                count=10,
            )

            assert len(after) == 1

            idle_after = after[0]["time_since_delivered"]

            assert idle_after < idle_before

        finally:
            await redis.delete(DECISION_STREAM)
            await redis.aclose()

    asyncio.run(scenario())


def test_heartbeating_job_is_not_recovered_as_stale() -> None:
    async def scenario() -> None:
        redis = Redis.from_url(
            get_settings().redis_url,
            decode_responses=True,
        )

        try:
            await redis.delete(DECISION_STREAM)

            worker_a = DecisionJobQueue(
                redis,
                consumer_name=f"heartbeat-worker-a-{uuid4()}",
            )

            worker_b = DecisionJobQueue(
                redis,
                consumer_name=f"heartbeat-worker-b-{uuid4()}",
            )

            await worker_a.initialize()
            await worker_b.initialize()

            job = DecisionJob(
                job_id=uuid4(),
                decision_run_id=uuid4(),
            )

            await worker_a.enqueue(job)

            processing_job = await worker_a.claim()

            assert processing_job is not None

            await worker_a.heartbeat(processing_job)

            recovered, dead_lettered = (
                await worker_b.recover_stale_jobs(
                    lease_seconds=60,
                    max_attempts=3,
                )
            )

            assert recovered == 0
            assert dead_lettered == 0

            pending = await redis.xpending(
                DECISION_STREAM,
                DECISION_CONSUMER_GROUP,
            )

            assert pending["pending"] == 1
            assert len(pending["consumers"]) == 1

        finally:
            await redis.delete(DECISION_STREAM)
            await redis.aclose()

    asyncio.run(scenario())
