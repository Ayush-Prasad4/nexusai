from uuid import UUID

from app.domain.models import DecisionRun


class InMemoryDecisionRunRepository:
    def __init__(self) -> None:
        self.runs: dict[UUID, DecisionRun] = {}

    async def save(self, run: DecisionRun) -> DecisionRun:
        self.runs[run.id] = run
        return run

    async def get(self, run_id: UUID) -> DecisionRun | None:
        return self.runs.get(run_id)
