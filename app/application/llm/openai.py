from openai import AsyncOpenAI

from app.application.llm.protocol import LLMClient
from app.core.config import Settings


class OpenAILLMClient(LLMClient):
    def __init__(self, settings: Settings) -> None:
        if not settings.llm_api_key:
            raise ValueError("NEXUSAI_LLM_API_KEY is not configured.")

        self.client = AsyncOpenAI(
            api_key=settings.llm_api_key,
        )
        self.model = settings.llm_model

    async def generate(self, prompt: str) -> str:
        response = await self.client.responses.create(
            model=self.model,
            input=prompt,
            max_output_tokens=1024,
        )

        return response.output_text
