from app.application.agents.contracts import ResearchResult
from app.application.agents.inputs import ResearchInput
from app.application.agents.protocol import Agent
from app.application.llm.protocol import LLMClient


class ResearchAgent(Agent[ResearchInput, ResearchResult]):
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    async def run(self, input: ResearchInput) -> ResearchResult:
        prompt = (
            "You are the Research Agent in a multi-agent decision system.\n\n"
            f"Objective:\n{input.objective}\n\n"
            f"Context:\n{input.context or 'No additional context provided.'}\n\n"
            "Identify the key facts, considerations, and information that "
            "should be researched to support this decision. "
            "Return concise research findings, one finding per line."
        )

        response = await self.llm.generate(prompt)

        findings = [
            line.strip("- ").strip()
            for line in response.splitlines()
            if line.strip()
        ]

        return ResearchResult(
            findings=findings,
            sources=[],
        )
