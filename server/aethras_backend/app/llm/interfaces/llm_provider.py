"""LLM provider ABC — swappable language model backends."""

from abc import ABC, abstractmethod


class ILlmProvider(ABC):
    """Contract for LLM inference (Strategy pattern)."""

    @abstractmethod
    async def complete(self, prompt: str, max_tokens: int = 512) -> str:
        """Generate text completion from prompt."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Unique provider identifier."""
