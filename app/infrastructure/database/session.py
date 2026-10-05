from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings


def create_database_engine() -> AsyncEngine:
    settings = get_settings()

    return create_async_engine(
        settings.database_url,
        pool_pre_ping=True,
    )


engine = create_database_engine()

AsyncSessionFactory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)
