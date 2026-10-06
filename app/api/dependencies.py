from fastapi import Request

from app.domain.repositories import DecisionRunRepository, UserRepository
from app.infrastructure.database.session import AsyncSessionFactory
from app.infrastructure.redis.queue import DecisionJobQueue
from app.infrastructure.repositories.postgres import (
    PostgresDecisionRunRepository,
    PostgresUserRepository,
)


def get_decision_repository() -> DecisionRunRepository:
    return PostgresDecisionRunRepository(AsyncSessionFactory)


def get_decision_job_queue(request: Request) -> DecisionJobQueue:
    return DecisionJobQueue(request.app.state.redis)



def get_user_repository() -> UserRepository:
    return PostgresUserRepository(AsyncSessionFactory)
