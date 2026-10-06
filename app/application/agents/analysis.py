from app.application.agents.contracts import AnalysisResult
from app.application.agents.inputs import AnalysisInput
from app.application.agents.protocol import Agent
from app.application.llm.protocol import LLMClient
from app.application.llm.structured import parse_structured_response


class AnalysisAgent(Agent[AnalysisInput, AnalysisResult]):
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    async def run(self, input: AnalysisInput) -> AnalysisResult:
        research = "\n".join(
            f"- {item}" for item in input.research
        ) or "No research findings provided."

        prompt = (
            "You are the Analysis Agent in a multi-agent decision system.\n\n"
            f"Objective:\n{input.objective}\n\n"
            f"Context:\n{input.context or 'No additional context provided.'}\n\n"
            f"Research findings:\n{research}\n\n"
            "Analyze the research in relation to the objective. "
            "Identify conclusions and important assumptions.\n\n"
            "Return ONLY valid JSON matching this schema:\n"
            '{"conclusions": ["conclusion 1"], "assumptions": ["assumption 1"]}\n\n'
            "Do not include markdown, code fences, or any text outside the JSON."
        )

        response = await self.llm.generate(prompt)

        return parse_structured_response(
            response,
            AnalysisResult,
        )
