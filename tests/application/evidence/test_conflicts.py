from app.application.evidence.conflicts import (
    ConflictReport,
    ConflictSeverity,
    EvidenceConflict,
)
from app.application.evidence.contracts import EvidenceItem


def test_conflict_report_defaults_to_empty() -> None:
    report = ConflictReport()

    assert report.conflicts == []


def test_evidence_conflict_contract() -> None:
    first = EvidenceItem(
        claim="Revenue increased by 18%.",
        source="Annual filing",
        source_type="regulatory_filing",
        confidence=0.9,
    )

    second = EvidenceItem(
        claim="Revenue declined by 7%.",
        source="Quarterly filing",
        source_type="regulatory_filing",
        confidence=0.8,
    )

    conflict = EvidenceConflict(
        first_evidence=first,
        second_evidence=second,
        reason="The evidence reports opposite revenue trends.",
        severity=ConflictSeverity.HIGH,
    )

    assert conflict.first_evidence.claim == "Revenue increased by 18%."
    assert conflict.second_evidence.claim == "Revenue declined by 7%."
    assert conflict.severity == ConflictSeverity.HIGH
