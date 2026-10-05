import asyncio
from uuid import uuid4

from redis import Redis

from app.application.jobs.contracts import DecisionJob
from app.core.config import get_settings
from app.infrastructure.redis.queue import DECISION_QUEUE
from app.workers import decision_worker


def create_test_redis_client() -> Redis:
    settings = get_settings()

    return Redis.from_url(
        settings.redis_url,
        decode_responses=True,
    )


def test_worker_consumes_decision_job(monkeypatch) -> None:
    redis = create_test_redis_client()
    redis.delete(DECISION_QUEUE)

    job = DecisionJob(
        job_id=uuid4(),
        decision_run_id=uuid4(),
    )

    redis.rpush(
        DECISION_QUEUE,
        job.model_dump_json(),
    )

    processed_jobs: list[DecisionJob] = []

    async def fake_process_job(job: DecisionJob) -> None:
        processed_jobs.append(job)

    monkeypatch.setattr(
        decision_worker,
        "process_job",
        fake_process_job,
    )

    async def consume_one_job() -> None:
        worker_redis = decision_worker.create_worker_redis_client()

        try:
            _, payload = await worker_redis.blpop(
                DECISION_QUEUE,
                timeout=2,
            )

            assert payload is not None

            received_job = DecisionJob.model_validate_json(payload)

            await decision_worker.process_job(received_job)
        finally:
            await worker_redis.aclose()

    asyncio.run(consume_one_job())

    assert len(processed_jobs) == 1
    assert processed_jobs[0].job_id == job.job_id
    assert processed_jobs[0].decision_run_id == job.decision_run_id
    assert processed_jobs[0].job_type == "decision.process"

    redis.delete(DECISION_QUEUE)
    redis.close()
