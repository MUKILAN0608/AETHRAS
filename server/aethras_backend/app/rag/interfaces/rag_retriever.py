"""RAG retriever ABC — lore and context retrieval."""

from abc import ABC, abstractmethod


class IRagRetriever(ABC):
    """Contract for retrieval-augmented generation."""

    @abstractmethod
    async def retrieve(self, query: str, world_id: str, top_k: int = 5) -> list[dict]:
        """Retrieve relevant lore chunks for a query."""
