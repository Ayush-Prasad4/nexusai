from app.application.agents.analysis import AnalysisAgent
from app.application.agents.critic import CriticAgent
from app.application.agents.inputs import (
    AnalysisInput,
    CritiqueInput,
    SynthesisInput,
)
from app.application.agents.synthesis import SynthesisAgent
from app.application.llm.fake import FakeLLMClient


async def test_analysis_agent_uses_structured_llm_response() -> None:
    llm = FakeLLMClient(
        response=(
            '{"conclusions": ["Conclusion one", "Conclusion two"], '
            '"assumptions": ["Assumption one"]}'
        )
    )

    agent = AnalysisAgent(llm)

    result = await agent.run(
        AnalysisInput(
            objective="Evaluate enterprise expansion",
            context="NexusAI targets European customers.",
            research=["Enterprise demand is growing."],
        )
    )

    assert result.conclusions == [
        "Conclusion one",
        "Conclusion two",
    ]
    assert result.assumptions == ["Assumption one"]
    assert len(llm.prompts) == 1
    assert "Enterprise demand is growing." in llm.prompts[0]


async def test_critic_agent_uses_structured_llm_response() -> None:
    llm = FakeLLMClient(
        response=(
            '{"concerns": ["Concern one", "Concern two"], '
            '"weaknesses": ["Weakness one"]}'
        )
    )

    agent = CriticAgent(llm)

    result = await agent.run(
        CritiqueInput(
            objective="Evaluate enterprise expansion",
            analysis=["Enterprise demand is growing."],
            assumptions=["Demand will continue growing."],
        )
    )

    assert result.concerns == [
        "Concern one",
        "Concern two",
    ]
    assert result.weaknesses == ["Weakness one"]
    assert len(llm.prompts) == 1
    assert "Enterprise demand is growing." in llm.prompts[0]


async def test_synthesis_agent_uses_structured_llm_response() -> None:
    llm = FakeLLMClient(
        response=(
            '{"decision": "Expand into enterprise customers", '
            '"rationale": ["Strong market demand", '
            '"Requires additional sales capacity"]}'
        )
    )

    agent = SynthesisAgent(llm)

    result = await agent.run(
        SynthesisInput(
            objective="Evaluate enterprise expansion",
            research=["Enterprise demand is growing."],
            analysis=["Expansion could increase revenue."],
            concerns=["Sales capacity may be insufficient."],
            weaknesses=[],
        )
    )

    assert result.decision == "Expand into enterprise customers"
    assert result.rationale == [
        "Strong market demand",
        "Requires additional sales capacity",
    ]
    assert len(llm.prompts) == 1
    assert "Expansion could increase revenue." in llm.prompts[0]
