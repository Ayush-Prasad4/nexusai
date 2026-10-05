from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph

from app.application.workflows.multi_agent_graph import (
    run_analysis,
    run_critique,
    run_research,
    run_synthesis,
)
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
    graph.add_node("research", run_research)
    graph.add_node("analysis", run_analysis)
    graph.add_node("critique", run_critique)
    graph.add_node("synthesis", run_synthesis)
    graph.add_node("complete", complete_decision)

    graph.add_edge(START, "prepare")
    graph.add_edge("prepare", "research")
    graph.add_edge("research", "analysis")
    graph.add_edge("analysis", "critique")
    graph.add_edge("critique", "synthesis")
    graph.add_edge("synthesis", "complete")
    graph.add_edge("complete", END)

    return graph.compile(checkpointer=checkpointer)
