import asyncio
import logging

from redis.asyncio import Redis

from app.application.jobs.contracts import DecisionJob
from app.core.config import get_settings
from app.infrastructure.redis.queue import DECISION_QUEUE


logger = logging.getLogger(__name__)


def create_worker_redis_client() -> Redis:
    settings = get_settings()

    return Redis.from_url(
        settings.redis_url,
        decode_responses=True,
    )


async def process_job(job: DecisionJob) -> None:
    logger.info(
        "Processing decision job",
        extra={
            "job_id": str(job.job_id),
            "decision_run_id": str(job.decision_run_id),
            "job_type": job.job_type,
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
