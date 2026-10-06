from pydantic import BaseModel, Field

from app.application.evidence.contracts import EvidenceBundle


class ResearchInput(BaseModel):
    objective: str = Field(min_length=1, max_length=10_000)
    context: str | None = Field(default=None, max_length=50_000)


class AnalysisInput(BaseModel):
    objective: str = Field(min_length=1, max_length=10_000)
    context: str | None = Field(default=None, max_length=50_000)
    research: list[str] = Field(default_factory=list)
    evidence: EvidenceBundle = Field(default_factory=EvidenceBundle)


class CritiqueInput(BaseModel):
    objective: str = Field(min_length=1, max_length=10_000)
    analysis: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)


class SynthesisInput(BaseModel):
    objective: str = Field(min_length=1, max_length=10_000)
    research: list[str] = Field(default_factory=list)
    analysis: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
