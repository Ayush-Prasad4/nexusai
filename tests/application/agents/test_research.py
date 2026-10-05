from app.application.agents.inputs import ResearchInput
from app.application.agents.research import ResearchAgent
from app.application.llm.fake import FakeLLMClient


async def test_research_agent_uses_llm_response() -> None:
    llm = FakeLLMClient(
        response="- Finding one\n- Finding two"
    )
    agent = ResearchAgent(llm)

    result = await agent.run(
        ResearchInput(
            objective="Evaluate enterprise expansion",
            context="NexusAI is targeting European customers.",
        )
    )

    assert result.findings == ["Finding one", "Finding two"]
    assert len(llm.prompts) == 1
    assert "Evaluate enterprise expansion" in llm.prompts[0]
    assert "European customers" in llm.prompts[0]
