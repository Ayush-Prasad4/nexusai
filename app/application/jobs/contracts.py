from uuid import UUID

from pydantic import BaseModel


class DecisionJob(BaseModel):
    job_id: UUID
    decision_run_id: UUID
    job_type: str = "decision.process"
