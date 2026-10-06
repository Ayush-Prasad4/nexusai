from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph

from app.application.llm.protocol import LLMClient
from app.application.workflows.multi_agent_graph import (
    run_analysis,
    run_conflict_detection,
    run_critique,
    run_research,
    run_verification,
    run_synthesis,
)
from app.application.workflows.state import DecisionState


def prepare_decision(state: DecisionState) -> dict:
    return {"status": "prepared", "error": None}


def complete_decision(state: DecisionState) -> dict:
    return {"status": "completed"}


def build_decision_graph(
    *,
    checkpointer: BaseCheckpointSaver | None = None,
    llm: LLMClient,
):
    async def research_node(state: DecisionState) -> dict:
        return await run_research(state, llm)

    async def verification_node(state: DecisionState) -> dict:
        return await run_verification(state)

    async def conflict_detection_node(state: DecisionState) -> dict:
        return await run_conflict_detection(state)

    async def analysis_node(state: DecisionState) -> dict:
        return await run_analysis(state, llm)

    async def critique_node(state: DecisionState) -> dict:
        return await run_critique(state, llm)

    async def synthesis_node(state: DecisionState) -> dict:
        return await run_synthesis(state, llm)

    graph = StateGraph(DecisionState)

    graph.add_node("prepare", prepare_decision)
    graph.add_node("research", research_node)
    graph.add_node("verification", verification_node)
    graph.add_node("conflict_detection", conflict_detection_node)
    graph.add_node("analysis", analysis_node)
    graph.add_node("critique", critique_node)
    graph.add_node("synthesis", synthesis_node)
    graph.add_node("complete", complete_decision)

    graph.add_edge(START, "prepare")
    graph.add_edge("prepare", "research")
    graph.add_edge("research", "verification")
    graph.add_edge("verification", "conflict_detection")
    graph.add_edge("conflict_detection", "analysis")
    graph.add_edge("analysis", "critique")
    graph.add_edge("critique", "synthesis")
    graph.add_edge("synthesis", "complete")
    graph.add_edge("complete", END)

    return graph.compile(checkpointer=checkpointer)
