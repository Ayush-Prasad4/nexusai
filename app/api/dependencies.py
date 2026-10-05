from functools import lru_cache

from app.domain.repositories import DecisionRunRepository
from app.infrastructure.repositories.in_memory import (
    InMemoryDecisionRunRepository,
)


@lru_cache
def get_decision_repository() -> DecisionRunRepository:
    return InMemoryDecisionRunRepository()
