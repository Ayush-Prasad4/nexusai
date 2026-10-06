from app.application.agents.inputs import ResearchInput
from app.application.agents.research import ResearchAgent
from app.application.llm.fake import FakeLLMClient


async def test_research_agent_uses_structured_llm_response() -> None:
    llm = FakeLLMClient(
        response=(
            '{"findings": ["Finding one", "Finding two"], '
            '"sources": ["source-a"]}'
        )
    )

    agent = ResearchAgent(llm)

    result = await agent.run(
        ResearchInput(
            objective="Evaluate enterprise expansion",
            context="NexusAI is targeting European customers.",
        )
    )

    assert result.findings == [
        "Finding one",
        "Finding two",
    ]
    assert result.sources == ["source-a"]

    assert len(llm.prompts) == 1
    assert "Evaluate enterprise expansion" in llm.prompts[0]
    assert "European customers" in llm.prompts[0]
    assert "valid JSON" in llm.prompts[0]
