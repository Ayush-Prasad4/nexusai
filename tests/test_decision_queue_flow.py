from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from redis.asyncio import Redis

from app.api.auth import get_current_user
from app.application.jobs.contracts import DecisionJob
from app.core.config import get_settings
from app.domain.models import User
from app.infrastructure.redis.queue import (
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

        test_user = User(
            id=uuid4(),
            email="queue-test@nexusai.test",
            password_hash="hashed-password",
            role="user",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        async def override_get_current_user() -> User:
            return test_user

        try:
            await redis.delete(DECISION_STREAM)

            queue = DecisionJobQueue(
                redis,
                consumer_name=f"test-worker-{uuid4()}",
            )

            await queue.initialize()

            app.dependency_overrides[get_current_user] = (
                override_get_current_user
            )

            try:
                with TestClient(app) as client:
                    response = client.post(
                        "/v1/decisions",
                        json={
                            "objective": (
                                "Verify asynchronous decision processing."
                            ),
                        },
                    )
            finally:
                app.dependency_overrides.pop(
                    get_current_user,
                    None,
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
            app.dependency_overrides.pop(
                get_current_user,
                None,
            )

            await redis.delete(DECISION_STREAM)
            await redis.delete(
                "nexusai:jobs:decision:dead-letter",
            )
            await redis.aclose()

    import asyncio

    asyncio.run(scenario())
