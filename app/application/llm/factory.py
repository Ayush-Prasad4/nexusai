from app.application.llm.openai import OpenAILLMClient
from app.application.llm.protocol import LLMClient
from app.core.config import Settings, get_settings


def get_llm_client(
    settings: Settings | None = None,
) -> LLMClient:
    settings = settings or get_settings()

    if settings.llm_provider == "openai":
        return OpenAILLMClient(settings)

    raise ValueError(
        f"Unsupported LLM provider: {settings.llm_provider}"
    )
