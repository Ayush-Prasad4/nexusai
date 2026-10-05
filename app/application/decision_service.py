from datetime import datetime, timezone
from uuid import uuid4

from app.application.jobs.contracts import DecisionJob
from app.domain.models import DecisionRequest, DecisionRun
from app.domain.repositories import DecisionRunRepository
from app.infrastructure.redis.queue import DecisionJobQueue


class DecisionService:
    def __init__(
        self,
        repository: DecisionRunRepository,
        job_queue: DecisionJobQueue,
    ) -> None:
        self.repository = repository
        self.job_queue = job_queue

    async def create_decision(
        self,
        request: DecisionRequest,
    ) -> DecisionRun:
        now = datetime.now(timezone.utc)

        run = DecisionRun(
            objective=request.objective,
            context=request.context,
            created_at=now,
            updated_at=now,
        )

        saved_run = await self.repository.save(run)

        job = DecisionJob(
            job_id=uuid4(),
            decision_run_id=saved_run.id,
        )

        await self.job_queue.enqueue(job)

        return saved_run
