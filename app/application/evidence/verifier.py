from app.application.evidence.contracts import (
    EvidenceItem,
    EvidenceVerification,
    VerificationStatus,
)


class EvidenceVerifier:
    MIN_CONFIDENCE = 0.5

    def verify(self, evidence: EvidenceItem) -> EvidenceVerification:
        if evidence.confidence < self.MIN_CONFIDENCE:
            return EvidenceVerification(
                status=VerificationStatus.REJECTED,
                reason=(
                    "Evidence confidence is below the minimum "
                    "verification threshold."
                ),
            )

        return EvidenceVerification(
            status=VerificationStatus.VERIFIED,
            reason="Evidence passed deterministic verification checks.",
        )
