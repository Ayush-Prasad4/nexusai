import asyncio
from uuid import uuid4

from app.application.workflows.multi_agent_graph import (
    build_multi_agent_graph,
)


def test_multi_agent_graph_executes_all_agents() -> None:
    async def scenario() -> None:
        graph = build_multi_agent_graph()

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

        assert len(result["research"]) == 1
        assert len(result["analysis"]) == 1
        assert len(result["critique"]) == 1
        assert result["synthesis"]
        assert result["status"] == "completed"

    asyncio.run(scenario())
