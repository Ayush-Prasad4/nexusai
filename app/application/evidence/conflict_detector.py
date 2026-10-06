import re

from app.application.evidence.conflicts import (
    ConflictReport,
    ConflictSeverity,
    EvidenceConflict,
)
from app.application.evidence.contracts import EvidenceItem


class ConflictDetector:
    POSITIVE_TERMS = {
        "increase",
        "increased",
        "increasing",
        "growth",
        "grew",
        "rose",
        "risen",
        "up",
    }

    NEGATIVE_TERMS = {
        "decrease",
        "decreased",
        "decline",
        "declined",
        "declining",
        "fell",
        "fallen",
        "down",
        "loss",
    }

    def detect(self, evidence: list[EvidenceItem]) -> ConflictReport:
        conflicts: list[EvidenceConflict] = []

        for index, first in enumerate(evidence):
            for second in evidence[index + 1:]:
                if self._is_direct_conflict(first.claim, second.claim):
                    conflicts.append(
                        EvidenceConflict(
                            first_evidence=first,
                            second_evidence=second,
                            reason=(
                                "The evidence contains opposing directional "
                                "claims about the same subject."
                            ),
                            severity=self._severity(first, second),
                        )
                    )

        return ConflictReport(conflicts=conflicts)

    def _is_direct_conflict(self, first_claim: str, second_claim: str) -> bool:
        first_direction = self._direction(first_claim)
        second_direction = self._direction(second_claim)

        if first_direction is None or second_direction is None:
            return False

        return first_direction != second_direction

    def _direction(self, claim: str) -> str | None:
        words = set(re.findall(r"\b[a-z]+\b", claim.lower()))

        has_positive = bool(words & self.POSITIVE_TERMS)
        has_negative = bool(words & self.NEGATIVE_TERMS)

        if has_positive and not has_negative:
            return "positive"

        if has_negative and not has_positive:
            return "negative"

        return None

    def _severity(
        self,
        first: EvidenceItem,
        second: EvidenceItem,
    ) -> ConflictSeverity:
        if first.confidence >= 0.8 and second.confidence >= 0.8:
            return ConflictSeverity.HIGH

        if first.confidence >= 0.6 and second.confidence >= 0.6:
            return ConflictSeverity.MEDIUM

        return ConflictSeverity.LOW
