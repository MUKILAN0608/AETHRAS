"""Narrative engine ABC — orchestrates RAG, prompt, LLM, validation pipeline."""

from abc import ABC, abstractmethod


class INarrativeEngine(ABC):
    """Contract for the narrative generation pipeline."""

    @abstractmethod
    async def generate_dialogue(self, request: dict) -> dict:
        """Generate adaptive NPC dialogue from player context."""

    @abstractmethod
    async def generate_environmental_narrative(self, request: dict) -> dict:
        """Generate environmental storytelling content."""
