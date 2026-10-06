import asyncio
from uuid import uuid4

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.application.llm.fake import FakeLLMClient
from app.application.workflows.decision_graph import build_decision_graph
from app.application.workflows.state import DecisionState
from app.core.config import get_settings


class DecisionCheckpointFakeLLM(FakeLLMClient):
    async def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)

        if "Research Agent" in prompt:
            return '{"findings":["Research finding"],"sources":["test-source"]}'

        if "Analysis Agent" in prompt:
            return '{"conclusions":["Analysis conclusion"],"assumptions":["Analysis assumption"]}'

        if "Critic Agent" in prompt:
            return '{"concerns":["Critique concern"],"weaknesses":["Critique weakness"]}'

        if "Synthesis Agent" in prompt:
            return '{"decision":"Proceed with the decision","rationale":["Supporting rationale"]}'

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
                "context": "Phase 5.8 integration test.",
                "status": "pending",
                "error": None,
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

            checkpoint = await checkpointer.aget_tuple(config)

            assert checkpoint is not None
            assert checkpoint.config["configurable"]["thread_id"] == thread_id

    asyncio.run(run_test())
