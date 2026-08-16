"""Memory graph ABC — player choice and consequence persistence."""

from abc import ABC, abstractmethod


class IMemoryGraph(ABC):
    """Contract for player memory graph operations."""

    @abstractmethod
    async def record_choice(self, session_id: str, choice: dict) -> bool:
        """Record a permanent player choice."""

    @abstractmethod
    async def sync_memory(self, session_id: str, active_tags: list[str]) -> list[str]:
        """Sync and return updated active memory tags."""

    @abstractmethod
    async def get_consequences(self, session_id: str, world_id: str) -> list[str]:
        """Get active consequence tags for a world."""
