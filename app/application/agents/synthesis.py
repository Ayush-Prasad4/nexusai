from app.application.agents.contracts import SynthesisResult
from app.application.agents.inputs import SynthesisInput
from app.application.agents.protocol import Agent
from app.application.llm.protocol import LLMClient


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
            "Synthesize the available information into a final decision. "
            "Return the decision as the first line, followed by concise "
            "rationale points, one per line."
        )

        response = await self.llm.generate(prompt)

        lines = [
            line.strip("- ").strip()
            for line in response.splitlines()
            if line.strip()
        ]

        decision = lines[0] if lines else "No decision generated."
        rationale = lines[1:]

        return SynthesisResult(
            decision=decision,
            rationale=rationale,
        )
