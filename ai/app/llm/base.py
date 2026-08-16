"""LLM provider abstraction."""

from abc import ABC, abstractmethod
from typing import Any, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMProvider(ABC):
    """Abstract LLM provider — swap MockLLM for Qwen without redesigning pipeline."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Unique provider identifier."""

    @abstractmethod
    async def generate(self, system: str, user: str) -> str:
        """Generate raw text completion."""

    @abstractmethod
    async def generate_structured(self, system: str, user: str, schema: type[T]) -> T:
        """Generate structured output matching a Pydantic schema."""

    @abstractmethod
    async def health(self) -> dict[str, Any]:
        """Provider health check."""
