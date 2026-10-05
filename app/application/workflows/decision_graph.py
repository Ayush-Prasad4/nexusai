from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph

from app.application.workflows.state import DecisionState


def prepare_decision(state: DecisionState) -> dict:
    return {
        "status": "prepared",
        "error": None,
    }


def complete_decision(state: DecisionState) -> dict:
    return {
        "status": "completed",
    }


def build_decision_graph(
    checkpointer: BaseCheckpointSaver | None = None,
):
    graph = StateGraph(DecisionState)

    graph.add_node("prepare", prepare_decision)
    graph.add_node("complete", complete_decision)

    graph.add_edge(START, "prepare")
    graph.add_edge("prepare", "complete")
    graph.add_edge("complete", END)

    return graph.compile(checkpointer=checkpointer)
