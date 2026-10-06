from app.application.evidence.contracts import (
    EvidenceItem,
    VerificationStatus,
)
from app.application.evidence.verifier import EvidenceVerifier


def test_verifier_accepts_high_confidence_evidence() -> None:
    evidence = EvidenceItem(
        claim="Enterprise demand is increasing.",
        source="SEC filing",
        source_type="regulatory_filing",
        confidence=0.9,
    )

    result = EvidenceVerifier().verify(evidence)

    assert result.status == VerificationStatus.VERIFIED
    assert "passed" in result.reason.lower()


def test_verifier_rejects_low_confidence_evidence() -> None:
    evidence = EvidenceItem(
        claim="Enterprise demand is increasing.",
        source="Market report",
        source_type="market_report",
        confidence=0.3,
    )

    result = EvidenceVerifier().verify(evidence)

    assert result.status == VerificationStatus.REJECTED
    assert "confidence" in result.reason.lower()


def test_verifier_accepts_boundary_confidence() -> None:
    evidence = EvidenceItem(
        claim="Enterprise demand is stable.",
        source="Company filing",
        source_type="regulatory_filing",
        confidence=0.5,
    )

    result = EvidenceVerifier().verify(evidence)

    assert result.status == VerificationStatus.VERIFIED
