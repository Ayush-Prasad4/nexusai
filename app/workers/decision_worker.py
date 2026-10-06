import asyncio
import logging
from uuid import uuid4

from redis.asyncio import Redis

from app.application.jobs.contracts import DecisionJob
from app.application.llm.factory import get_llm_client
from app.application.reliability.executor import execute_with_retry
from app.application.reliability.retry import RetryPolicy
from app.application.workflows.decision_graph import build_decision_graph
from app.core.config import get_settings
from app.domain.repositories import DecisionRunRepository
from app.domain.status import DecisionRunStatus
from app.infrastructure.database.checkpointer import create_checkpoint_saver
from app.infrastructure.database.session import AsyncSessionFactory
from app.infrastructure.redis.queue import (
    DecisionJobQueue,
)
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
        config = {
            "configurable": {
                "thread_id": str(decision_run.id),
            }
        }

        latest_checkpoint = await checkpointer.aget_tuple(config)

        if latest_checkpoint is not None:
            channel_values = latest_checkpoint.checkpoint.get(
                "channel_values",
                {},
            )

            if channel_values.get("status") == "completed":
                logger.info(
                    "Decision workflow already completed; skipping duplicate job",
                    extra={
                        "job_id": str(job.job_id),
                        "decision_run_id": str(job.decision_run_id),
                    },
                )
                return

        llm = get_llm_client()

        graph = build_decision_graph(
            checkpointer=checkpointer,
            llm=llm,
        )

        initial_state = {
            "decision_run_id": decision_run.id,
            "objective": decision_run.objective,
            "context": decision_run.context,
            "status": decision_run.status.value,
            "error": None,
        }

        async def execute_workflow() -> dict:
            return await graph.ainvoke(
                initial_state,
                config=config,
            )

        result = await execute_with_retry(
            execute_workflow,
            RetryPolicy(),
        )

    await repository.update_status(
        decision_run.id,
        DecisionRunStatus.COMPLETED,
    )

    logger.info(
        "Decision workflow completed",
        extra={
            "job_id": str(job.job_id),
            "decision_run_id": str(job.decision_run_id),
            "status": result["status"],
        },
    )


async def heartbeat_processing_job(
    queue: DecisionJobQueue,
    processing_job,
    interval_seconds: float,
) -> None:
    while True:
        await asyncio.sleep(interval_seconds)
        await queue.heartbeat(processing_job)


async def run_worker() -> None:
    redis = create_worker_redis_client()

    try:
        logger.info("Decision worker started")

        queue = DecisionJobQueue(
            redis,
            consumer_name=f"worker-{uuid4()}",
        )

        await queue.initialize()

        logger.info(
            "Decision job consumer group initialized",
        )

        while True:
            processing_job = await queue.claim()

            if processing_job is None:
                continue

            job = processing_job.job
            settings = get_settings()

            heartbeat_interval = max(
                settings.job_lease_seconds / 3,
                1.0,
            )

            heartbeat_task = asyncio.create_task(
                heartbeat_processing_job(
                    queue,
                    processing_job,
                    heartbeat_interval,
                )
            )

            try:
                await process_job(job)
            except Exception:
                logger.exception(
                    "Decision job failed; leaving stream message pending",
                    extra={
                        "job_id": str(job.job_id),
                        "decision_run_id": str(job.decision_run_id),
                    },
                )
                raise
            finally:
                heartbeat_task.cancel()

                try:
                    await heartbeat_task
                except asyncio.CancelledError:
                    pass

            await queue.acknowledge(processing_job)

    finally:
        await redis.aclose()


if __name__ == "__main__":
    asyncio.run(run_worker())
