from app.application.agents.contracts import AnalysisResult
from app.application.agents.inputs import AnalysisInput
from app.application.agents.protocol import Agent
from app.application.llm.protocol import LLMClient


class AnalysisAgent(Agent[AnalysisInput, AnalysisResult]):
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    async def run(self, input: AnalysisInput) -> AnalysisResult:
        research = "\n".join(
            f"- {finding}" for finding in input.research
        ) or "No research findings provided."

        prompt = (
            "You are the Analysis Agent in a multi-agent decision system.\n\n"
            f"Objective:\n{input.objective}\n\n"
            f"Context:\n{input.context or 'No additional context provided.'}\n\n"
            f"Research findings:\n{research}\n\n"
            "Analyze the research findings in relation to the objective. "
            "Identify the main conclusions and important assumptions. "
            "Return conclusions first, one per line, followed by assumptions, "
            "one per line."
        )

        response = await self.llm.generate(prompt)

        lines = [
            line.strip("- ").strip()
            for line in response.splitlines()
            if line.strip()
        ]

        return AnalysisResult(
            conclusions=lines,
            assumptions=[],
        )
