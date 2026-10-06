from app.application.evidence.conflict_detector import ConflictDetector
from app.application.evidence.conflicts import ConflictSeverity
from app.application.evidence.contracts import EvidenceItem


def make_evidence(claim: str, confidence: float = 0.9) -> EvidenceItem:
    return EvidenceItem(
        claim=claim,
        source="Test source",
        source_type="test",
        confidence=confidence,
    )


def test_detector_finds_opposing_trends() -> None:
    evidence = [
        make_evidence("Revenue increased by 18%."),
        make_evidence("Revenue declined by 7%."),
    ]

    report = ConflictDetector().detect(evidence)

    assert len(report.conflicts) == 1
    assert report.conflicts[0].severity == ConflictSeverity.HIGH


def test_detector_does_not_flag_same_direction() -> None:
    evidence = [
        make_evidence("Revenue increased by 18%."),
        make_evidence("Revenue increased by 5%."),
    ]

    report = ConflictDetector().detect(evidence)

    assert report.conflicts == []


def test_detector_uses_medium_severity_for_moderate_confidence() -> None:
    evidence = [
        make_evidence("Revenue increased by 18%.", confidence=0.7),
        make_evidence("Revenue declined by 7%.", confidence=0.7),
    ]

    report = ConflictDetector().detect(evidence)

    assert len(report.conflicts) == 1
    assert report.conflicts[0].severity == ConflictSeverity.MEDIUM


def test_detector_uses_low_severity_for_low_confidence() -> None:
    evidence = [
        make_evidence("Revenue increased by 18%.", confidence=0.55),
        make_evidence("Revenue declined by 7%.", confidence=0.55),
    ]

    report = ConflictDetector().detect(evidence)

    assert len(report.conflicts) == 1
    assert report.conflicts[0].severity == ConflictSeverity.LOW


def test_detector_ignores_claims_without_direction() -> None:
    evidence = [
        make_evidence("Revenue was 100 million euros."),
        make_evidence("Revenue was 120 million euros."),
    ]

    report = ConflictDetector().detect(evidence)

    assert report.conflicts == []
