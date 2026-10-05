from app.application.agents.contracts import CritiqueResult
from app.application.agents.inputs import CritiqueInput
from app.application.agents.protocol import Agent
from app.application.llm.protocol import LLMClient


class CriticAgent(Agent[CritiqueInput, CritiqueResult]):
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    async def run(self, input: CritiqueInput) -> CritiqueResult:
        analysis = "\n".join(
            f"- {item}" for item in input.analysis
        ) or "No analysis conclusions provided."

        assumptions = "\n".join(
            f"- {item}" for item in input.assumptions
        ) or "No assumptions provided."

        prompt = (
            "You are the Critic Agent in a multi-agent decision system.\n\n"
            f"Objective:\n{input.objective}\n\n"
            f"Analysis:\n{analysis}\n\n"
            f"Assumptions:\n{assumptions}\n\n"
            "Critically review the analysis. Identify concerns, unsupported "
            "claims, missing considerations, and weaknesses. "
            "Return one concern or weakness per line."
        )

        response = await self.llm.generate(prompt)

        concerns = [
            line.strip("- ").strip()
            for line in response.splitlines()
            if line.strip()
        ]

        return CritiqueResult(
            concerns=concerns,
            weaknesses=[],
        )
