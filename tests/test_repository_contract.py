import asyncio
from datetime import datetime, timezone
from uuid import uuid4

from app.domain.models import DecisionRun
from app.domain.status import DecisionRunStatus
from app.domain.repositories import DecisionRunRepository


class FakeDecisionRunRepository:
    def __init__(self) -> None:
        self.runs: dict[str, DecisionRun] = {}

    async def save(self, run: DecisionRun) -> DecisionRun:
        self.runs[str(run.id)] = run
        return run

    async def get(self, run_id):
        return self.runs.get(str(run_id))

    async def update_status(
        self,
        run_id,
        status: DecisionRunStatus,
    ) -> None:
        run = self.runs.get(str(run_id))

        if run is None:
            raise ValueError(f"Decision run not found: {run_id}")

        run.status = status
        run.updated_at = datetime.now(timezone.utc)


def test_repository_implements_contract() -> None:
    repository = FakeDecisionRunRepository()

    assert isinstance(repository, DecisionRunRepository)


def test_repository_save_and_get() -> None:
    async def scenario() -> None:
        repository = FakeDecisionRunRepository()

        now = datetime.now(timezone.utc)
        run = DecisionRun(
            id=uuid4(),
            objective="Assess supplier reliability.",
            context="Supplier has experienced repeated delivery delays.",
            created_at=now,
            updated_at=now,
        )

        saved = await repository.save(run)
        retrieved = await repository.get(run.id)

        assert saved == run
        assert retrieved == run

    asyncio.run(scenario())
