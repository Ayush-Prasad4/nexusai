import asyncio
from uuid import uuid4

from app.application.workflows.decision_graph import (
    build_decision_graph,
)


def test_decision_graph_completes_workflow() -> None:
    async def scenario() -> None:
        graph = build_decision_graph()

        state = {
            "decision_run_id": uuid4(),
            "objective": "Test durable decision workflow",
            "context": None,
            "status": "pending",
            "error": None,
            "research": [],
            "analysis": [],
            "critique": [],
            "synthesis": None,
        }

        result = await graph.ainvoke(state)

        assert result["status"] == "completed"
        assert len(result["research"]) == 1
        assert len(result["analysis"]) == 1
        assert len(result["critique"]) == 1
        assert result["synthesis"]

    asyncio.run(scenario())
