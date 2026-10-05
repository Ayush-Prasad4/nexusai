from app.application.agents.contracts import SynthesisResult
from app.application.agents.inputs import SynthesisInput
from app.application.agents.protocol import Agent


class SynthesisAgent(Agent[SynthesisInput, SynthesisResult]):
    async def run(self, input: SynthesisInput) -> SynthesisResult:
        decision = (
            f"Decision synthesized for objective: {input.objective}"
        )

        rationale = [
            f"Considered {len(input.research)} research finding(s).",
            f"Considered {len(input.analysis)} analysis conclusion(s).",
            f"Considered {len(input.concerns)} critique concern(s).",
        ]

        return SynthesisResult(
            decision=decision,
            rationale=rationale,
        )
