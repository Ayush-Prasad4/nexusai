import asyncio
from uuid import uuid4

from redis import Redis

from app.application.jobs.contracts import DecisionJob
from app.application.workflows.state import DecisionState
from app.core.config import get_settings
from app.domain.models import DecisionRunStatus
from app.infrastructure.redis.queue import (
    DECISION_STREAM,
    DecisionJobQueue,
)
from app.workers import decision_worker


def create_test_redis_client() -> Redis:
    settings = get_settings()
    return Redis.from_url(
        settings.redis_url,
        decode_responses=True,
    )


def test_worker_consumes_decision_job(monkeypatch) -> None:
    async def scenario() -> None:
        redis = decision_worker.create_worker_redis_client()

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

            await queue.enqueue(job)

            received_jobs: list[DecisionJob] = []

            async def fake_process_job(
                received_job: DecisionJob,
            ) -> None:
                received_jobs.append(received_job)

            monkeypatch.setattr(
                decision_worker,
                "process_job",
                fake_process_job,
            )

            processing_job = await queue.claim()

            assert processing_job is not None

            await decision_worker.process_job(
                processing_job.job,
            )

            await queue.acknowledge(
                processing_job,
            )

            assert received_jobs == [job]

        finally:
            await redis.delete(DECISION_STREAM)
            await redis.aclose()

    asyncio.run(scenario())


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

    class FakeCheckpointer:
        async def aget_tuple(self, config):
            return None


    class FakeCheckpointContext:
        async def __aenter__(self):
            return FakeCheckpointer()

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

    assert len(received_checkpointers) == 1
    assert hasattr(
        received_checkpointers[0],
        "aget_tuple",
    )
    assert len(invoked_states) == 1

    state = invoked_states[0]

    assert state["decision_run_id"] == decision_run_id
    assert state["objective"] == "Test worker decision"
    assert state["context"] == "Test context"
    assert state["status"] == "pending"
    assert state["error"] is None


def test_process_job_skips_already_completed_workflow(
    monkeypatch,
) -> None:
    decision_run_id = uuid4()

    job = DecisionJob(
        job_id=uuid4(),
        decision_run_id=decision_run_id,
    )

    class FakeDecisionRun:
        id = decision_run_id
        objective = "Already completed decision"
        context = "Duplicate job test"
        status = DecisionRunStatus.PENDING

    class FakeRepository:
        async def get(self, run_id):
            assert run_id == decision_run_id
            return FakeDecisionRun()

    graph_called = False

    class FakeGraph:
        async def ainvoke(self, state, *, config):
            nonlocal graph_called
            graph_called = True
            return {
                **state,
                "status": "completed",
            }

    class FakeCheckpointer:
        async def aget_tuple(self, config):
            return type(
                "Checkpoint",
                (),
                {
                    "checkpoint": {
                        "channel_values": {
                            "status": "completed",
                        }
                    }
                },
            )()

    class FakeCheckpointContext:
        async def __aenter__(self):
            return FakeCheckpointer()

        async def __aexit__(self, exc_type, exc, tb):
            return False

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
        lambda *, checkpointer: FakeGraph(),
    )

    asyncio.run(
        decision_worker.process_job(job)
    )

    assert graph_called is False
