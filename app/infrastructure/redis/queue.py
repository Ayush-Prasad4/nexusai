from uuid import uuid4

from redis.asyncio import Redis

from app.application.jobs.contracts import DecisionJob
from app.application.jobs.dead_letter import DeadLetterJob
from app.application.jobs.processing import ProcessingJob


DECISION_STREAM = "nexusai:jobs:decision"
DECISION_CONSUMER_GROUP = "nexusai-workers"
DECISION_DLQ = "nexusai:jobs:decision:dead-letter"


class DecisionJobQueue:
    def __init__(
        self,
        redis: Redis,
        consumer_name: str | None = None,
    ) -> None:
        self.redis = redis
        self.consumer_name = (
            consumer_name
            or f"worker-{uuid4()}"
        )

    async def initialize(self) -> None:
        try:
            await self.redis.xgroup_create(
                name=DECISION_STREAM,
                groupname=DECISION_CONSUMER_GROUP,
                id="0",
                mkstream=True,
            )
        except Exception as exc:
            if "BUSYGROUP" not in str(exc):
                raise

    async def enqueue(
        self,
        job: DecisionJob,
    ) -> str:
        return await self.redis.xadd(
            DECISION_STREAM,
            {
                "job": job.model_dump_json(),
            },
        )

    async def claim(self) -> ProcessingJob | None:
        messages = await self.redis.xreadgroup(
            groupname=DECISION_CONSUMER_GROUP,
            consumername=self.consumer_name,
            streams={
                DECISION_STREAM: ">",
            },
            count=1,
            block=1000,
        )

        if not messages:
            return None

        _, stream_messages = messages[0]
        stream_id, fields = stream_messages[0]

        job = DecisionJob.model_validate_json(
            fields["job"],
        )

        return ProcessingJob.create(
            job,
            stream_id=stream_id,
        )

    async def acknowledge(
        self,
        processing_job: ProcessingJob,
    ) -> None:
        if processing_job.stream_id is None:
            raise ValueError(
                "Cannot acknowledge a job without a stream ID."
            )

        await self.redis.xack(
            DECISION_STREAM,
            DECISION_CONSUMER_GROUP,
            processing_job.stream_id,
        )

    async def dead_letter(
        self,
        processing_job: ProcessingJob,
        reason: str,
    ) -> None:
        dead_letter_job = DeadLetterJob(
            job=processing_job.job,
            attempts=processing_job.attempt,
            reason=reason,
        )

        await self.redis.rpush(
            DECISION_DLQ,
            dead_letter_job.model_dump_json(),
        )

        await self.acknowledge(processing_job)

    async def recover_stale_jobs(
        self,
        lease_seconds: float,
        max_attempts: int,
    ) -> tuple[int, int]:
        recovered = 0
        dead_lettered = 0

        start_id = "0-0"

        while True:
            result = await self.redis.xautoclaim(
                name=DECISION_STREAM,
                groupname=DECISION_CONSUMER_GROUP,
                consumername=self.consumer_name,
                min_idle_time=int(lease_seconds * 1000),
                start_id=start_id,
                count=100,
            )

            next_start_id, messages, *_ = result

            for stream_id, fields in messages:
                job = DecisionJob.model_validate_json(
                    fields["job"],
                )

                processing_job = ProcessingJob.create(
                    job,
                    stream_id=stream_id,
                )

                if processing_job.attempt >= max_attempts:
                    await self.dead_letter(
                        processing_job,
                        "maximum delivery attempts exceeded",
                    )
                    dead_lettered += 1
                    continue

                next_job = processing_job.next_attempt()

                await self.enqueue(
                    next_job.job,
                )

                await self.acknowledge(
                    processing_job,
                )

                recovered += 1

            if next_start_id == "0-0":
                break

            start_id = next_start_id

        return recovered, dead_lettered
