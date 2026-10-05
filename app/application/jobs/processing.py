from datetime import datetime, timezone

from pydantic import BaseModel

from app.application.jobs.contracts import DecisionJob


class ProcessingJob(BaseModel):
    job: DecisionJob
    claimed_at: datetime
    attempt: int = 1
    stream_id: str | None = None

    @classmethod
    def create(
        cls,
        job: DecisionJob,
        stream_id: str | None = None,
    ) -> "ProcessingJob":
        return cls(
            job=job,
            claimed_at=datetime.now(timezone.utc),
            attempt=job.attempt,
            stream_id=stream_id,
        )

    def is_stale(
        self,
        lease_seconds: float,
    ) -> bool:
        now = datetime.now(timezone.utc)

        age = (
            now - self.claimed_at
        ).total_seconds()

        return age >= lease_seconds

    def next_attempt(self) -> "ProcessingJob":
        next_job = self.job.model_copy(
            update={
                "attempt": self.attempt + 1,
            }
        )

        return ProcessingJob.create(next_job)
