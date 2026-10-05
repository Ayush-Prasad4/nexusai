from typing import TypedDict
from uuid import UUID


class DecisionState(TypedDict):
    decision_run_id: UUID
    objective: str
    context: str | None
    status: str
    error: str | None

    research: list[str]
    analysis: list[str]
    critique: list[str]
    synthesis: str | None
