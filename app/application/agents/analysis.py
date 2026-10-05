from app.application.agents.contracts import AnalysisResult
from app.application.agents.inputs import AnalysisInput
from app.application.agents.protocol import Agent


class AnalysisAgent(Agent[AnalysisInput, AnalysisResult]):
    async def run(self, input: AnalysisInput) -> AnalysisResult:
        conclusion = (
            f"Analysis derived from {len(input.research)} research finding(s) "
            f"for objective: {input.objective}"
        )

        return AnalysisResult(
            conclusions=[conclusion],
            assumptions=[],
        )
