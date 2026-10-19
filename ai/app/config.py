"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, SecretStr, model_validator
from urllib.parse import urlparse
from typing import Literal
from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """AETHRAS AI service settings."""

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        hide_input_in_errors=True,
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

    aethras_decision_provider: Literal["cloudflare_clef_flash"] = "cloudflare_clef_flash"
    aethras_decision_enabled: bool = False
    cloudflare_account_id: str = Field(default="", repr=False)
    cloudflare_auth_token: SecretStr = SecretStr("")
    cloudflare_clef_model: Literal["@cf/cloudflare/clef-flash"] = "@cf/cloudflare/clef-flash"
    cloudflare_clef_api_base_url: str = "https://api.cloudflare.com/client/v4"
    aethras_decision_timeout_seconds: float = Field(default=3, gt=0, le=10)
    aethras_decision_max_retries: int = Field(default=0, ge=0, le=2)
    decision_min_confidence: float = Field(default=0.7, ge=0, le=1)
    decision_selection_min_margin: float = Field(default=0.1, ge=0, le=1)
    decision_review_threshold: float = Field(default=0.5, ge=0, le=1)
    decision_simulation_threshold: float = Field(default=0.5, ge=0, le=1)

    @property
    def decision_model(self) -> str:
        return self.cloudflare_clef_model

    @property
    def decision_api_url(self) -> str:
        return (f"{self.cloudflare_clef_api_base_url.rstrip('/')}/accounts/"
                f"{self.cloudflare_account_id}/ai/run/{self.cloudflare_clef_model}")

    @property
    def decision_configured(self) -> bool:
        return bool(re.fullmatch(r"[a-fA-F0-9]{32}", self.cloudflare_account_id)
                    and self.cloudflare_auth_token.get_secret_value().strip())

    @model_validator(mode="after")
    def validate_decision(self):
        url = urlparse(self.cloudflare_clef_api_base_url)
        if url.scheme != "https" or not url.hostname or url.username or url.password or url.query or url.fragment:
            raise ValueError("Cloudflare API base must use HTTPS without credentials, query, or fragment")
        if self.aethras_decision_enabled and not self.decision_configured:
            raise ValueError("Enabled Clef-Flash requires a 32-character hexadecimal CLOUDFLARE_ACCOUNT_ID and nonempty CLOUDFLARE_AUTH_TOKEN")
        return self


settings = Settings()
