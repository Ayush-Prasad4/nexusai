import pytest
from pydantic import ValidationError

from app.application.evidence.contracts import (
    EvidenceBundle,
    EvidenceItem,
    EvidenceStance,
)


def test_evidence_item_accepts_valid_data() -> None:
    evidence = EvidenceItem(
        claim="Enterprise demand is increasing.",
        source="SEC filing",
        source_type="regulatory_filing",
        stance=EvidenceStance.SUPPORTS,
        confidence=0.92,
    )

    assert evidence.claim == "Enterprise demand is increasing."
    assert evidence.source == "SEC filing"
    assert evidence.source_type == "regulatory_filing"
    assert evidence.stance == EvidenceStance.SUPPORTS
    assert evidence.confidence == 0.92


def test_evidence_item_rejects_invalid_confidence() -> None:
    with pytest.raises(ValidationError):
        EvidenceItem(
            claim="Test claim",
            source="Test source",
            source_type="test",
            confidence=1.5,
        )


def test_evidence_item_supports_contradicting_stance() -> None:
    evidence = EvidenceItem(
        claim="Enterprise demand is declining.",
        source="Market report",
        source_type="market_report",
        stance=EvidenceStance.CONTRADICTS,
        confidence=0.75,
    )

    assert evidence.stance == EvidenceStance.CONTRADICTS


def test_evidence_bundle_contains_items() -> None:
    bundle = EvidenceBundle(
        items=[
            EvidenceItem(
                claim="Claim one",
                source="Source one",
                source_type="report",
                confidence=0.8,
            ),
            EvidenceItem(
                claim="Claim two",
                source="Source two",
                source_type="filing",
                confidence=0.9,
            ),
        ]
    )

    assert len(bundle.items) == 2
    assert bundle.items[0].claim == "Claim one"
    assert bundle.items[1].claim == "Claim two"


def test_evidence_bundle_defaults_to_empty() -> None:
    bundle = EvidenceBundle()

    assert bundle.items == []
