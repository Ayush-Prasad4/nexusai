from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "NexusAI"
    environment: str = "development"
    api_v1_prefix: str = "/v1"
    database_url: str = (
        "postgresql+asyncpg://nexusai:nexusai@localhost:5432/nexusai"
    )
    redis_url: str = "redis://localhost:6379/0"
    job_lease_seconds: float = 60.0
    max_job_attempts: int = 3
    llm_provider: str = "openai"
    llm_model: str = "gpt-5.4-mini"
    llm_api_key: str | None = None

    model_config = SettingsConfigDict(
        env_prefix="NEXUSAI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
