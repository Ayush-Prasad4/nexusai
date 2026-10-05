from uuid import uuid4

from app.application.jobs.contracts import DecisionJob
from app.application.jobs.dead_letter import DeadLetterJob


def test_dead_letter_job_records_failure_metadata() -> None:
    job = DecisionJob(
        job_id=uuid4(),
        decision_run_id=uuid4(),
    )

    dead_letter = DeadLetterJob(
        job=job,
        attempts=3,
        reason="maximum delivery attempts exceeded",
    )

    assert dead_letter.job == job
    assert dead_letter.attempts == 3
    assert dead_letter.reason == (
        "maximum delivery attempts exceeded"
    )
