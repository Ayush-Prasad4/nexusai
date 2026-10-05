from langgraph.graph import END, START, StateGraph

from app.application.agents.analysis import AnalysisAgent
from app.application.agents.critic import CriticAgent
from app.application.agents.inputs import (
    AnalysisInput,
    CritiqueInput,
    ResearchInput,
    SynthesisInput,
)
from app.application.agents.research import ResearchAgent
from app.application.agents.synthesis import SynthesisAgent
from app.application.workflows.state import DecisionState


async def run_research(state: DecisionState) -> dict:
    agent = ResearchAgent()

    result = await agent.run(
        ResearchInput(
            objective=state["objective"],
            context=state["context"],
        )
    )

    return {
        "research": result.findings,
    }


async def run_analysis(state: DecisionState) -> dict:
    agent = AnalysisAgent()

    result = await agent.run(
        AnalysisInput(
            objective=state["objective"],
            context=state["context"],
            research=state.get("research", []),
        )
    )

    return {
        "analysis": result.conclusions,
    }


async def run_critique(state: DecisionState) -> dict:
    agent = CriticAgent()

    result = await agent.run(
        CritiqueInput(
            objective=state["objective"],
            analysis=state.get("analysis", []),
            assumptions=[],
        )
    )

    return {
        "critique": result.concerns,
    }


async def run_synthesis(state: DecisionState) -> dict:
    agent = SynthesisAgent()

    result = await agent.run(
        SynthesisInput(
            objective=state["objective"],
            research=state.get("research", []),
            analysis=state.get("analysis", []),
            concerns=state.get("critique", []),
            weaknesses=[],
        )
    )

    return {
        "synthesis": result.decision,
        "status": "completed",
    }


def build_multi_agent_graph():
    graph = StateGraph(DecisionState)

    graph.add_node("research", run_research)
    graph.add_node("analysis", run_analysis)
    graph.add_node("critique", run_critique)
    graph.add_node("synthesis", run_synthesis)

    graph.add_edge(START, "research")
    graph.add_edge("research", "analysis")
    graph.add_edge("analysis", "critique")
    graph.add_edge("critique", "synthesis")
    graph.add_edge("synthesis", END)

    return graph.compile()
