from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "NexusAI"
    environment: str = Field(default="development", pattern="^(development|testing|production)$")
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
    jwt_secret_key: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60
    max_request_body_bytes: int = 1_048_576
    allowed_hosts: list[str] = [
        "localhost",
        "127.0.0.1",
        "testserver",
    ]

    model_config = SettingsConfigDict(
        env_prefix="NEXUSAI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
