"""Mock LLM provider — deterministic rule-based inference for development."""

from typing import Any, TypeVar

from pydantic import BaseModel

from app.llm.base import LLMProvider

T = TypeVar("T", bound=BaseModel)


class MockLLM(LLMProvider):
    """Mock LLM using deterministic pattern matching. No model weights loaded."""

    @property
    def provider_id(self) -> str:
        return "mock"

    async def generate(self, system: str, user: str) -> str:
        return f"[mock response for: {user[:80]}]"

    async def generate_structured(self, system: str, user: str, schema: type[T]) -> T:
        # Pipeline stages use direct Python logic; this satisfies the interface.
        raise NotImplementedError("MockLLM uses pipeline modules directly, not structured generation")

    async def health(self) -> dict[str, Any]:
        return {"provider": "mock", "status": "ok", "model_loaded": False}
