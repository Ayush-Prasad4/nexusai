from app.application.agents.inputs import ResearchInput
from app.application.agents.research import ResearchAgent
from app.application.evidence.contracts import EvidenceStance
from app.application.llm.fake import FakeLLMClient


async def test_research_agent_uses_structured_llm_response() -> None:
    llm = FakeLLMClient(
        response=(
            '{"findings": ["Finding one", "Finding two"], '
            '"evidence": {"items": ['
            '{"claim": "Finding one", '
            '"source": "source-a", '
            '"source_type": "market_report", '
            '"stance": "supports", '
            '"confidence": 0.9, '
            '"metadata": {}}'
            ']}}'
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

    assert len(result.evidence.items) == 1

    evidence = result.evidence.items[0]

    assert evidence.claim == "Finding one"
    assert evidence.source == "source-a"
    assert evidence.source_type == "market_report"
    assert evidence.stance == EvidenceStance.SUPPORTS
    assert evidence.confidence == 0.9

    assert len(llm.prompts) == 1
    assert "Evaluate enterprise expansion" in llm.prompts[0]
    assert "European customers" in llm.prompts[0]
    assert "valid JSON" in llm.prompts[0]
    assert "evidence" in llm.prompts[0]
