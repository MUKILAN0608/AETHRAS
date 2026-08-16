"""Qwen LLM provider stub — connect in Phase 4."""

from typing import Any, TypeVar

from pydantic import BaseModel

from app.llm.base import LLMProvider

T = TypeVar("T", bound=BaseModel)


class QwenLLM(LLMProvider):
    """Stub for Qwen3.6-35B-A3B integration (Phase 4)."""

    def __init__(self, model_name: str = "Qwen3.6-35B-A3B") -> None:
        self._model_name = model_name

    @property
    def provider_id(self) -> str:
        return "qwen"

    async def generate(self, system: str, user: str) -> str:
        raise NotImplementedError("Qwen integration is Phase 4 — use MockLLM")

    async def generate_structured(self, system: str, user: str, schema: type[T]) -> T:
        raise NotImplementedError("Qwen integration is Phase 4 — use MockLLM")

    async def health(self) -> dict[str, Any]:
        return {"provider": "qwen", "status": "not_configured", "model": self._model_name}
