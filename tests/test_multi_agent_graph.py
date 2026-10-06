import asyncio
from uuid import uuid4

from app.application.llm.fake import FakeLLMClient
from app.application.workflows.multi_agent_graph import build_multi_agent_graph


class MultiAgentFakeLLM(FakeLLMClient):
    async def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)

        if "Research Agent" in prompt:
            return (
                '{"findings": ["Research finding"], '
                '"sources": ["test-source"]}'
            )

        if "Analysis Agent" in prompt:
            return (
                '{"conclusions": ["Analysis conclusion"], '
                '"assumptions": ["Analysis assumption"]}'
            )

        if "Critic Agent" in prompt:
            return (
                '{"concerns": ["Critique concern"], '
                '"weaknesses": ["Critique weakness"]}'
            )

        if "Synthesis Agent" in prompt:
            return (
                '{"decision": "Proceed with the decision", '
                '"rationale": ["Supporting rationale"]}'
            )

        raise AssertionError("Unknown agent prompt")


def test_multi_agent_graph_executes_all_agents() -> None:
    async def scenario() -> None:
        llm = MultiAgentFakeLLM()

        graph = build_multi_agent_graph(llm=llm)

        result = await graph.ainvoke(
            {
                "decision_run_id": uuid4(),
                "objective": "Evaluate whether a new product should be launched.",
                "context": "The product targets European customers.",
                "status": "pending",
                "error": None,
                "research": [],
                "analysis": [],
                "critique": [],
                "synthesis": None,
            }
        )

        assert result["research"] == ["Research finding"]
        assert result["analysis"] == ["Analysis conclusion"]
        assert result["critique"] == ["Critique concern"]
        assert result["synthesis"] == "Proceed with the decision"
        assert result["status"] == "completed"

        assert len(llm.prompts) == 4

    asyncio.run(scenario())
