from app.application.agents.contracts import CritiqueResult
from app.application.agents.inputs import CritiqueInput
from app.application.agents.protocol import Agent
from app.application.llm.protocol import LLMClient
from app.application.llm.structured import parse_structured_response


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
            "Critically review the analysis. Identify concerns and "
            "weaknesses, including unsupported claims or missing considerations.\n\n"
            "Return ONLY valid JSON matching this schema:\n"
            '{"concerns": ["concern 1"], "weaknesses": ["weakness 1"]}\n\n'
            "Do not include markdown, code fences, or any text outside the JSON."
        )

        response = await self.llm.generate(prompt)

        return parse_structured_response(
            response,
            CritiqueResult,
        )
