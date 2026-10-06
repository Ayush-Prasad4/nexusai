from typing import Protocol, runtime_checkable
from uuid import UUID

from app.domain.models import DecisionRun, User
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


@runtime_checkable
class UserRepository(Protocol):
    async def create(self, user: User) -> User:
        ...

    async def get_by_id(self, user_id: UUID) -> User | None:
        ...

    async def get_by_email(self, email: str) -> User | None:
        ...
