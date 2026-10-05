from pydantic import BaseModel

from app.application.jobs.contracts import DecisionJob


class DeadLetterJob(BaseModel):
    job: DecisionJob
    attempts: int
    reason: str
