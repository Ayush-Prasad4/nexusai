import asyncio
from uuid import uuid4

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.application.evidence.contracts import EvidenceBundle
from app.application.llm.fake import FakeLLMClient
from app.application.workflows.decision_graph import build_decision_graph
from app.application.workflows.state import DecisionState
from app.core.config import get_settings


class DecisionCheckpointFakeLLM(FakeLLMClient):
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


def get_checkpoint_connection_string() -> str:
    settings = get_settings()

    return settings.database_url.replace(
        "postgresql+asyncpg://",
        "postgresql://",
    )


def test_decision_workflow_persists_checkpoint() -> None:
    async def run_test() -> None:
        thread_id = str(uuid4())

        async with AsyncPostgresSaver.from_conn_string(
            get_checkpoint_connection_string(),
        ) as checkpointer:
            graph = build_decision_graph(
                checkpointer=checkpointer,
                llm=DecisionCheckpointFakeLLM(),
            )

            state: DecisionState = {
                "decision_run_id": uuid4(),
                "objective": "Verify durable LangGraph checkpointing.",
                "context": "Phase 7.1 evidence integration test.",
                "status": "pending",
                "error": None,
                "research": [],
                "evidence": EvidenceBundle(),
                "analysis": [],
                "critique": [],
                "synthesis": None,
            }

            config = {
                "configurable": {
                    "thread_id": thread_id,
                }
            }

            result = await graph.ainvoke(
                state,
                config=config,
            )

            assert result["status"] == "completed"
            assert len(result["evidence"].items) == 1
            assert result["evidence"].items[0].claim == "Research finding"

            checkpoint = await checkpointer.aget_tuple(config)

            assert checkpoint is not None
            assert checkpoint.config["configurable"]["thread_id"] == thread_id

            checkpoint_state = checkpoint.checkpoint["channel_values"]

            assert "evidence" in checkpoint_state
            assert len(checkpoint_state["evidence"].items) == 1
            assert (
                checkpoint_state["evidence"].items[0].claim
                == "Research finding"
            )

    asyncio.run(run_test())
