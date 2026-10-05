from typing import Protocol, runtime_checkable
from uuid import UUID

from app.domain.models import DecisionRun
from app.domain.status import DecisionRunStatus


@runtime_checkable
class DecisionRunRepository(Protocol):
    async def save(self, run: DecisionRun) -> DecisionRun:
        ...

    async def get(self, run_id: UUID) -> DecisionRun | None:
        ...

    async def update_status(
        self,
        run_id: UUID,
        status: DecisionRunStatus,
    ) -> None:
        ...
