import asyncio
from datetime import datetime, timezone

from sqlalchemy import delete

from app.domain.models import DecisionRun
from app.infrastructure.database.models import DecisionRunModel
from app.infrastructure.database.session import AsyncSessionFactory, engine
from app.infrastructure.repositories.postgres import PostgresDecisionRunRepository


def test_postgres_repository_persistence() -> None:
    asyncio.run(_test_postgres_repository_persistence())


async def _test_postgres_repository_persistence() -> None:
    repository = PostgresDecisionRunRepository(AsyncSessionFactory)

    now = datetime.now(timezone.utc)

    run = DecisionRun(
        objective="PostgreSQL repository integration test",
        context="NexusAI",
        created_at=now,
        updated_at=now,
    )

    saved = await repository.save(run)

    try:
        loaded = await repository.get(saved.id)

        assert loaded is not None
        assert loaded.id == saved.id
        assert loaded.status == saved.status
        assert loaded.objective == saved.objective
        assert loaded.context == saved.context
        assert loaded.created_at == saved.created_at
        assert loaded.updated_at == saved.updated_at
    finally:
        async with AsyncSessionFactory() as session:
            await session.execute(
                delete(DecisionRunModel).where(
                    DecisionRunModel.id == saved.id
                )
            )
            await session.commit()

        await engine.dispose()
