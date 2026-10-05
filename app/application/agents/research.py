from app.application.agents.contracts import ResearchResult
from app.application.agents.inputs import ResearchInput
from app.application.agents.protocol import Agent


class ResearchAgent(Agent[ResearchInput, ResearchResult]):
    async def run(self, input: ResearchInput) -> ResearchResult:
        finding = f"Research required for objective: {input.objective}"

        return ResearchResult(
            findings=[finding],
            sources=[],
        )
