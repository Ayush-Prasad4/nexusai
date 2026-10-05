import asyncio
from datetime import datetime, timezone
from uuid import UUID

from app.application.decision_service import DecisionService
from app.domain.models import DecisionRequest, DecisionRun


class FakeDecisionRunRepository:
    def __init__(self) -> None:
        self.saved_run: DecisionRun | None = None

    async def save(self, run: DecisionRun) -> DecisionRun:
        self.saved_run = run
        return run

    async def get(self, run_id: UUID) -> DecisionRun | None:
        return self.saved_run


def test_create_decision() -> None:
    async def scenario() -> None:
        repository = FakeDecisionRunRepository()
        service = DecisionService(repository)

        request = DecisionRequest(
            objective="Assess supplier reliability.",
        )

        run = await service.create_decision(request)

        assert isinstance(run.id, UUID)
        assert run.status.value == "pending"
        assert run.created_at.tzinfo is not None
        assert run.updated_at.tzinfo is not None
        assert repository.saved_run == run

    asyncio.run(scenario())
