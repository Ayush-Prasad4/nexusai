from pydantic import BaseModel, Field

from app.application.evidence.contracts import EvidenceBundle


class ResearchResult(BaseModel):
    findings: list[str] = Field(default_factory=list)
    evidence: EvidenceBundle = Field(default_factory=EvidenceBundle)


class AnalysisResult(BaseModel):
    conclusions: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)


class CritiqueResult(BaseModel):
    concerns: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)


class SynthesisResult(BaseModel):
    decision: str = Field(min_length=1)
    rationale: list[str] = Field(default_factory=list)
