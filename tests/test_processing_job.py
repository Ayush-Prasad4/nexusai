from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.application.jobs.contracts import DecisionJob
from app.application.jobs.processing import ProcessingJob


def test_processing_job_records_claim_metadata() -> None:
    job = DecisionJob(
        job_id=uuid4(),
        decision_run_id=uuid4(),
    )

    processing_job = ProcessingJob.create(job)

    assert processing_job.job == job
    assert processing_job.attempt == 1
    assert processing_job.claimed_at.tzinfo is not None


def test_processing_job_detects_stale_lease() -> None:
    job = DecisionJob(
        job_id=uuid4(),
        decision_run_id=uuid4(),
    )

    processing_job = ProcessingJob(
        job=job,
        claimed_at=datetime.now(timezone.utc)
        - timedelta(seconds=120),
        attempt=1,
    )

    assert processing_job.is_stale(
        lease_seconds=60,
    ) is True


def test_processing_job_accepts_active_lease() -> None:
    job = DecisionJob(
        job_id=uuid4(),
        decision_run_id=uuid4(),
    )

    processing_job = ProcessingJob.create(job)

    assert processing_job.is_stale(
        lease_seconds=60,
    ) is False
