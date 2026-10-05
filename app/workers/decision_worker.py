import asyncio
import logging

from redis.asyncio import Redis

from app.application.jobs.contracts import DecisionJob
from app.application.workflows.decision_graph import build_decision_graph
from app.core.config import get_settings
from app.domain.repositories import DecisionRunRepository
from app.infrastructure.database.checkpointer import create_checkpoint_saver
from app.infrastructure.database.session import AsyncSessionFactory
from app.infrastructure.redis.queue import DECISION_QUEUE
from app.infrastructure.repositories.postgres import (
    PostgresDecisionRunRepository,
)

logger = logging.getLogger(__name__)


def create_worker_redis_client() -> Redis:
    settings = get_settings()
    return Redis.from_url(
        settings.redis_url,
        decode_responses=True,
    )


def create_worker_decision_repository() -> DecisionRunRepository:
    return PostgresDecisionRunRepository(AsyncSessionFactory)


async def process_job(job: DecisionJob) -> None:
    logger.info(
        "Processing decision job",
        extra={
            "job_id": str(job.job_id),
            "decision_run_id": str(job.decision_run_id),
            "job_type": job.job_type,
        },
    )

    repository = create_worker_decision_repository()
    decision_run = await repository.get(job.decision_run_id)

    if decision_run is None:
        raise ValueError(
            f"Decision run not found: {job.decision_run_id}"
        )

    async with create_checkpoint_saver() as checkpointer:
        graph = build_decision_graph(
            checkpointer=checkpointer,
        )

        initial_state = {
            "decision_run_id": decision_run.id,
            "objective": decision_run.objective,
            "context": decision_run.context,
            "status": decision_run.status.value,
            "error": None,
        }

        config = {
            "configurable": {
                "thread_id": str(decision_run.id),
            }
        }

        result = await graph.ainvoke(
            initial_state,
            config=config,
        )

    logger.info(
        "Decision workflow completed",
        extra={
            "job_id": str(job.job_id),
            "decision_run_id": str(job.decision_run_id),
            "status": result["status"],
        },
    )


async def run_worker() -> None:
    redis = create_worker_redis_client()

    try:
        logger.info("Decision worker started")

        while True:
            _, payload = await redis.blpop(DECISION_QUEUE)

            job = DecisionJob.model_validate_json(payload)

            await process_job(job)

    finally:
        await redis.aclose()


if __name__ == "__main__":
    asyncio.run(run_worker())
