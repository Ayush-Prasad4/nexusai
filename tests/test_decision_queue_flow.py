from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from redis.asyncio import Redis

from app.application.jobs.contracts import DecisionJob
from app.core.config import get_settings
from app.infrastructure.redis.queue import (
    DECISION_CONSUMER_GROUP,
    DECISION_STREAM,
    DecisionJobQueue,
)
from app.main import app


def test_create_decision_enqueues_job() -> None:
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

            with TestClient(app) as client:
                response = client.post(
                    "/v1/decisions",
                    json={
                        "objective": (
                            "Verify asynchronous decision processing."
                        ),
                    },
                )

            assert response.status_code == 201

            body = response.json()
            decision_run_id = UUID(body["id"])

            messages = await redis.xrange(
                DECISION_STREAM,
                count=10,
            )

            assert messages

            matching_jobs: list[DecisionJob] = []

            for _, fields in messages:
                job = DecisionJob.model_validate_json(
                    fields["job"],
                )

                if job.decision_run_id == decision_run_id:
                    matching_jobs.append(job)

            assert len(matching_jobs) == 1
            assert matching_jobs[0].job_type == "decision.process"

        finally:
            await redis.delete(DECISION_STREAM)
            await redis.delete(
                "nexusai:jobs:decision:dead-letter",
            )
            await redis.aclose()

    import asyncio

    asyncio.run(scenario())
