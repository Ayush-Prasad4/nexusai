from app.domain.repositories import DecisionRunRepository
from app.infrastructure.database.session import AsyncSessionFactory
from app.infrastructure.repositories.postgres import (
    PostgresDecisionRunRepository,
)


def get_decision_repository() -> DecisionRunRepository:
    return PostgresDecisionRunRepository(AsyncSessionFactory)
