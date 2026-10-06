import asyncio
from uuid import uuid4

from app.application.evidence.contracts import EvidenceBundle, VerificationStatus
from app.application.llm.fake import FakeLLMClient
from app.application.workflows.decision_graph import build_decision_graph


class DecisionGraphFakeLLM(FakeLLMClient):
    async def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)

        if "Research Agent" in prompt:
            return (
                '{"findings":["Research finding"], '
                '"evidence":{"items":['
                '{"claim":"Research finding",'
                '"source":"test-source",'
                '"source_type":"test",'
                '"stance":"supports",'
                '"confidence":0.9,'
                '"metadata":{}}]}}'
            )

        if "Analysis Agent" in prompt:
            return (
                '{"conclusions":["Analysis conclusion"], '
                '"assumptions":["Analysis assumption"]}'
            )

        if "Critic Agent" in prompt:
            return (
                '{"concerns":["Critique concern"], '
                '"weaknesses":["Critique weakness"]}'
            )

        if "Synthesis Agent" in prompt:
            return (
                '{"decision":"Proceed with the decision", '
                '"rationale":["Supporting rationale"]}'
            )

        raise AssertionError("Unknown agent prompt")


def test_decision_graph_completes_workflow() -> None:
    async def scenario() -> None:
        llm = DecisionGraphFakeLLM()

        graph = build_decision_graph(llm=llm)

        state = {
            "decision_run_id": uuid4(),
            "objective": "Test durable decision workflow",
            "context": None,
            "status": "pending",
            "error": None,
            "research": [],
            "evidence": EvidenceBundle(),
            "analysis": [],
            "critique": [],
            "synthesis": None,
        }

        result = await graph.ainvoke(state)

        assert result["status"] == "completed"
        assert len(result["research"]) == 1
        assert len(result["evidence"].items) == 1
        assert result["evidence"].items[0].claim == "Research finding"
        assert result["evidence"].items[0].verification is not None
        assert (
            result["evidence"].items[0].verification.status
            == VerificationStatus.VERIFIED
        )
        assert len(result["analysis"]) == 1
        assert len(result["critique"]) == 1
        assert result["synthesis"] == "Proceed with the decision"

        assert len(llm.prompts) == 4

    asyncio.run(scenario())
