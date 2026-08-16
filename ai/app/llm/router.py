"""LLM provider router — selects Fast or Deep path provider."""

from app.config import settings
from app.llm.base import LLMProvider
from app.llm.mock import MockLLM
from app.llm.qwen import QwenLLM


def get_provider(mode: str = "fast") -> LLMProvider:
    """Return LLM provider for inference mode."""
    provider_name = settings.llm_provider
    if provider_name == "qwen" and mode == "deep":
        return QwenLLM(settings.qwen_model_name)
    return MockLLM()
