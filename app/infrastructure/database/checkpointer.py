from contextlib import asynccontextmanager
from typing import AsyncIterator

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.core.config import get_settings


def get_checkpoint_connection_string() -> str:
    settings = get_settings()

    return settings.database_url.replace(
        "postgresql+asyncpg://",
        "postgresql://",
    )


@asynccontextmanager
async def create_checkpoint_saver() -> AsyncIterator[AsyncPostgresSaver]:
    connection_string = get_checkpoint_connection_string()

    async with AsyncPostgresSaver.from_conn_string(
        connection_string,
    ) as checkpointer:
        yield checkpointer
