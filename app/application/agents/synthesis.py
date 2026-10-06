from app.application.agents.contracts import SynthesisResult
from app.application.agents.inputs import SynthesisInput
from app.application.agents.protocol import Agent
from app.application.llm.protocol import LLMClient
from app.application.llm.structured import parse_structured_response


class SynthesisAgent(Agent[SynthesisInput, SynthesisResult]):
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    async def run(self, input: SynthesisInput) -> SynthesisResult:
        research = "\n".join(
            f"- {item}" for item in input.research
        ) or "No research findings provided."

        analysis = "\n".join(
            f"- {item}" for item in input.analysis
        ) or "No analysis conclusions provided."

        concerns = "\n".join(
            f"- {item}" for item in input.concerns
        ) or "No critique concerns provided."

        prompt = (
            "You are the Synthesis Agent in a multi-agent decision system.\n\n"
            f"Objective:\n{input.objective}\n\n"
            f"Research:\n{research}\n\n"
            f"Analysis:\n{analysis}\n\n"
            f"Critique:\n{concerns}\n\n"
            "Synthesize the available information into a final decision "
            "and concise rationale.\n\n"
            "Return ONLY valid JSON matching this schema:\n"
            '{"decision": "final decision", "rationale": ["reason 1"]}\n\n'
            "Do not include markdown, code fences, or any text outside the JSON."
        )

        response = await self.llm.generate(prompt)

        return parse_structured_response(
            response,
            SynthesisResult,
        )
