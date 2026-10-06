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

        evidence = "\n".join(
            (
                f"- Claim: {item.claim}\n"
                f"  Source: {item.source}\n"
                f"  Source type: {item.source_type}\n"
                f"  Stance: {item.stance.value}\n"
                f"  Confidence: {item.confidence}"
            )
            for item in input.evidence.items
        ) or "No evidence provided."

        prompt = (
            "You are the Analysis Agent in a multi-agent decision system.\n\n"
            f"Objective:\n{input.objective}\n\n"
            f"Context:\n{input.context or 'No additional context provided.'}\n\n"
            f"Research findings:\n{research}\n\n"
            f"Evidence:\n{evidence}\n\n"
            "Analyze the research and evidence in relation to the objective. "
            "Distinguish supported conclusions from assumptions. "
            "Consider the source, stance, and confidence of each evidence item "
            "when forming conclusions.\n\n"
            "Return ONLY valid JSON matching this schema:\n"
            '{"conclusions": ["conclusion 1"], "assumptions": ["assumption 1"]}\n\n'
            "Do not include markdown, code fences, or any text outside the JSON."
        )

        response = await self.llm.generate(prompt)

        return parse_structured_response(
            response,
            AnalysisResult,
        )
