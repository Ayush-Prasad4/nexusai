from enum import Enum

from pydantic import BaseModel, Field


class EvidenceStance(str, Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    NEUTRAL = "neutral"


class EvidenceItem(BaseModel):
    claim: str = Field(min_length=1, max_length=10_000)
    source: str = Field(min_length=1, max_length=10_000)
    source_type: str = Field(min_length=1, max_length=100)
    stance: EvidenceStance = EvidenceStance.SUPPORTS
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: dict[str, str] = Field(default_factory=dict)


class EvidenceBundle(BaseModel):
    items: list[EvidenceItem] = Field(default_factory=list)
