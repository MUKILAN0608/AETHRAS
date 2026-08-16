"""Prompt engine ABC — template assembly and token budgeting."""

from abc import ABC, abstractmethod


class IPromptEngine(ABC):
    """Contract for prompt template rendering."""

    @abstractmethod
    def render(self, template_id: str, context: dict) -> str:
        """Render a prompt template with injected context."""

    @abstractmethod
    def estimate_tokens(self, prompt: str) -> int:
        """Estimate token count for budget enforcement."""
