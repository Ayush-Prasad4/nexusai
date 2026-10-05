import asyncio
from uuid import uuid4

from redis import Redis

from app.application.jobs.contracts import DecisionJob
from app.application.workflows.state import DecisionState
from app.core.config import get_settings
from app.domain.models import DecisionRunStatus
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

    received_jobs: list[DecisionJob] = []

    async def fake_process_job(received_job: DecisionJob) -> None:
        received_jobs.append(received_job)

    monkeypatch.setattr(
        decision_worker,
        "process_job",
        fake_process_job,
    )

    async def consume_once() -> None:
        worker_redis = decision_worker.create_worker_redis_client()

        try:
            _, payload = await worker_redis.blpop(DECISION_QUEUE)

            received_job = DecisionJob.model_validate_json(payload)

            await decision_worker.process_job(received_job)
        finally:
            await worker_redis.aclose()

    asyncio.run(consume_once())

    assert received_jobs == [job]

    redis.delete(DECISION_QUEUE)
    redis.close()


def test_process_job_executes_decision_graph(monkeypatch) -> None:
    decision_run_id = uuid4()

    job = DecisionJob(
        job_id=uuid4(),
        decision_run_id=decision_run_id,
    )

    class FakeDecisionRun:
        id = decision_run_id
        objective = "Test worker decision"
        context = "Test context"
        status = DecisionRunStatus.PENDING

    class FakeRepository:
        async def get(self, run_id):
            assert run_id == decision_run_id
            return FakeDecisionRun()

    invoked_states: list[dict] = []
    received_checkpointers: list[object] = []

    class FakeGraph:
        async def ainvoke(
            self,
            state: dict,
            *,
            config: dict,
        ) -> dict:
            invoked_states.append(state)
            return {
                **state,
                "status": "completed",
            }

    class FakeCheckpointContext:
        async def __aenter__(self):
            return "fake-checkpointer"

        async def __aexit__(self, exc_type, exc, tb):
            return False

    def fake_build_decision_graph(*, checkpointer):
        received_checkpointers.append(checkpointer)
        return FakeGraph()

    monkeypatch.setattr(
        decision_worker,
        "create_worker_decision_repository",
        lambda: FakeRepository(),
    )

    monkeypatch.setattr(
        decision_worker,
        "create_checkpoint_saver",
        lambda: FakeCheckpointContext(),
    )

    monkeypatch.setattr(
        decision_worker,
        "build_decision_graph",
        fake_build_decision_graph,
    )

    asyncio.run(
        decision_worker.process_job(job)
    )

    assert received_checkpointers == ["fake-checkpointer"]
    assert len(invoked_states) == 1

    state = invoked_states[0]

    assert state["decision_run_id"] == decision_run_id
    assert state["objective"] == "Test worker decision"
    assert state["context"] == "Test context"
    assert state["status"] == "pending"
    assert state["error"] is None
