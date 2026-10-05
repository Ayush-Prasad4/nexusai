from redis.asyncio import Redis

from app.application.jobs.contracts import DecisionJob


DECISION_QUEUE = "nexusai:jobs:decision"


class DecisionJobQueue:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def enqueue(self, job: DecisionJob) -> None:
        await self.redis.rpush(
            DECISION_QUEUE,
            job.model_dump_json(),
        )
