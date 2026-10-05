from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.models import DecisionRun
from app.domain.status import DecisionRunStatus
from app.infrastructure.database.mappers.decision_run import (
    to_domain,
    to_model,
)
from app.infrastructure.database.models import DecisionRunModel


class PostgresDecisionRunRepository:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self.session_factory = session_factory

    async def save(self, run: DecisionRun) -> DecisionRun:
        model = to_model(run)

        async with self.session_factory() as session:
            session.add(model)
            await session.commit()
            await session.refresh(model)

            return to_domain(model)

    async def update_status(
        self,
        run_id: UUID,
        status: DecisionRunStatus,
    ) -> None:
        async with self.session_factory() as session:
            result = await session.execute(
                select(DecisionRunModel).where(
                    DecisionRunModel.id == run_id
                )
            )

            model = result.scalar_one_or_none()

            if model is None:
                raise ValueError(
                    f"Decision run not found: {run_id}"
                )

            model.status = status.value
            model.updated_at = datetime.now(timezone.utc)

            await session.commit()

    async def get(self, run_id: UUID) -> DecisionRun | None:
        async with self.session_factory() as session:
            result = await session.execute(
                select(DecisionRunModel).where(
                    DecisionRunModel.id == run_id
                )
            )

            model = result.scalar_one_or_none()

            if model is None:
                return None

            return to_domain(model)
