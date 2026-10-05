import pytest

from app.application.llm.fake import FakeLLMClient
from app.application.llm.openai import OpenAILLMClient
from app.core.config import Settings


@pytest.mark.asyncio
async def test_fake_llm_client_returns_configured_response() -> None:
    client = FakeLLMClient(response="test response")

    result = await client.generate("test prompt")

    assert result == "test response"
    assert client.prompts == ["test prompt"]


def test_openai_llm_client_requires_api_key() -> None:
    settings = Settings(llm_api_key=None)

    with pytest.raises(
        ValueError,
        match="NEXUSAI_LLM_API_KEY is not configured",
    ):
        OpenAILLMClient(settings)
