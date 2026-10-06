from enum import Enum

from pydantic import BaseModel, Field

from app.application.evidence.contracts import EvidenceItem


class ConflictSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EvidenceConflict(BaseModel):
    first_evidence: EvidenceItem
    second_evidence: EvidenceItem
    reason: str = Field(min_length=1, max_length=10_000)
    severity: ConflictSeverity


class ConflictReport(BaseModel):
    conflicts: list[EvidenceConflict] = Field(default_factory=list)
