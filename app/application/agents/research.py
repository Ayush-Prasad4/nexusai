from app.application.agents.contracts import ResearchResult
from app.application.agents.inputs import ResearchInput
from app.application.agents.protocol import Agent
from app.application.llm.protocol import LLMClient
from app.application.llm.structured import parse_structured_response


class ResearchAgent(Agent[ResearchInput, ResearchResult]):
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    async def run(self, input: ResearchInput) -> ResearchResult:
        prompt = (
            "You are the Research Agent in a multi-agent decision system.\n\n"
            f"Objective:\n{input.objective}\n\n"
            f"Context:\n{input.context or 'No additional context provided.'}\n\n"
            "Identify the key facts, considerations, and information that "
            "should be researched to support this decision.\n\n"
            "Return ONLY valid JSON matching this schema:\n"
            '{"findings": ["finding 1", "finding 2"], "sources": []}\n\n'
            "Do not include markdown, code fences, or any text outside the JSON."
        )

        response = await self.llm.generate(prompt)

        return parse_structured_response(
            response,
            ResearchResult,
        )
