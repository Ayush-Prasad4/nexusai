from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("NEXUSAI_APP_NAME", "NexusAI")
    environment: str = os.getenv("NEXUSAI_ENV", "development")
    api_v1_prefix: str = "/v1"


settings = Settings()
