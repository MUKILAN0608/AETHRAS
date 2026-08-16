"""Narrative validator ABC — enforces canon and tone rules."""

from abc import ABC, abstractmethod


class INarrativeValidator(ABC):
    """Contract for post-generation narrative validation."""

    @abstractmethod
    async def validate(self, generated_text: str, context: dict) -> tuple[bool, list[str]]:
        """Return (is_valid, list_of_violation_reasons)."""
