from app.application.agents.contracts import CritiqueResult
from app.application.agents.inputs import CritiqueInput
from app.application.agents.protocol import Agent


class CriticAgent(Agent[CritiqueInput, CritiqueResult]):
    async def run(self, input: CritiqueInput) -> CritiqueResult:
        concern = (
            f"Review the analysis for unsupported assumptions "
            f"related to objective: {input.objective}"
        )

        return CritiqueResult(
            concerns=[concern],
            weaknesses=[],
        )
