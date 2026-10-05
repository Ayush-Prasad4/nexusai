from uuid import UUID

from fastapi.testclient import TestClient
from redis import Redis

from app.application.jobs.contracts import DecisionJob
from app.core.config import get_settings
from app.infrastructure.redis.queue import DECISION_QUEUE
from app.main import app


def create_test_redis_client() -> Redis:
    settings = get_settings()

    return Redis.from_url(
        settings.redis_url,
        decode_responses=True,
    )


def test_create_decision_enqueues_job() -> None:
    redis = create_test_redis_client()

    redis.delete(DECISION_QUEUE)

    with TestClient(app) as client:
        response = client.post(
            "/v1/decisions",
            json={
                "objective": "Verify asynchronous decision processing.",
            },
        )

    assert response.status_code == 201

    body = response.json()
    decision_run_id = UUID(body["id"])

    payload = redis.lpop(DECISION_QUEUE)

    assert payload is not None

    job = DecisionJob.model_validate_json(payload)

    assert job.decision_run_id == decision_run_id
    assert job.job_type == "decision.process"

    redis.delete(DECISION_QUEUE)
    redis.close()
