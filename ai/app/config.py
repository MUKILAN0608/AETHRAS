"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """AETHRAS AI service settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    service_name: str = "aethras-ai"
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "info"

    # LLM provider configuration
    llm_provider: str = "mock"
    qwen_model_name: str = "Qwen3.6-35B-A3B"

    # Future: LLM provider keys (not used in demo phase)
    openai_api_key: str | None = None


settings = Settings()
