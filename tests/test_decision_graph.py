from uuid import uuid4

from app.application.workflows.decision_graph import build_decision_graph


def test_decision_graph_completes_workflow() -> None:
    graph = build_decision_graph()

    state = {
        "decision_run_id": uuid4(),
        "objective": "Test durable decision workflow",
        "context": None,
        "status": "pending",
        "error": None,
    }

    result = graph.invoke(state)

    assert result["status"] == "completed"
    assert result["decision_run_id"] == state["decision_run_id"]
    assert result["objective"] == state["objective"]
    assert result["context"] == state["context"]
    assert result["error"] is None
