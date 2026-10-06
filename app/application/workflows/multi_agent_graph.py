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
from app.application.evidence.contracts import EvidenceBundle
from app.application.evidence.verifier import EvidenceVerifier
from app.application.llm.fake import FakeLLMClient
from app.application.llm.protocol import LLMClient
from app.application.workflows.state import DecisionState


def _default_llm() -> LLMClient:
    return FakeLLMClient()


async def run_research(
    state: DecisionState,
    llm: LLMClient,
) -> dict:
    agent = ResearchAgent(llm)

    result = await agent.run(
        ResearchInput(
            objective=state["objective"],
            context=state["context"],
        )
    )

    return {
        "research": result.findings,
        "evidence": result.evidence,
    }


async def run_verification(
    state: DecisionState,
) -> dict:
    verifier = EvidenceVerifier()

    verified_items = []

    for evidence in state["evidence"].items:
        verification = verifier.verify(evidence)

        verified_items.append(
            evidence.model_copy(
                update={"verification": verification}
            )
        )

    return {
        "evidence": EvidenceBundle(items=verified_items),
    }


async def run_analysis(
    state: DecisionState,
    llm: LLMClient,
) -> dict:
    agent = AnalysisAgent(llm)

    result = await agent.run(
        AnalysisInput(
            objective=state["objective"],
            context=state["context"],
            research=state.get("research", []),
            evidence=state["evidence"],
        )
    )

    return {
        "analysis": result.conclusions,
    }


async def run_critique(
    state: DecisionState,
    llm: LLMClient,
) -> dict:
    agent = CriticAgent(llm)

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


async def run_synthesis(
    state: DecisionState,
    llm: LLMClient,
) -> dict:
    agent = SynthesisAgent(llm)

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


def build_multi_agent_graph(
    llm: LLMClient | None = None,
):
    llm = llm or _default_llm()

    async def research_node(state: DecisionState) -> dict:
        return await run_research(state, llm)

    async def verification_node(state: DecisionState) -> dict:
        return await run_verification(state)

    async def analysis_node(state: DecisionState) -> dict:
        return await run_analysis(state, llm)

    async def critique_node(state: DecisionState) -> dict:
        return await run_critique(state, llm)

    async def synthesis_node(state: DecisionState) -> dict:
        return await run_synthesis(state, llm)

    graph = StateGraph(DecisionState)

    graph.add_node("research", research_node)
    graph.add_node("verification", verification_node)
    graph.add_node("analysis", analysis_node)
    graph.add_node("critique", critique_node)
    graph.add_node("synthesis", synthesis_node)

    graph.add_edge(START, "research")
    graph.add_edge("research", "verification")
    graph.add_edge("verification", "analysis")
    graph.add_edge("analysis", "critique")
    graph.add_edge("critique", "synthesis")
    graph.add_edge("synthesis", END)

    return graph.compile()
