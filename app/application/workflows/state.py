from typing import TypedDict
from uuid import UUID

from app.application.evidence.contracts import EvidenceBundle


class DecisionState(TypedDict):
    decision_run_id: UUID
    objective: str
    context: str | None
    status: str
    error: str | None

    research: list[str]
    evidence: EvidenceBundle
    analysis: list[str]
    critique: list[str]
    synthesis: str | None
