"""Vendor-neutral decision transport boundary and provider registry."""
from typing import Protocol
from app.decision_engine.schemas import ProviderResponse


class ProviderFailure(Exception):
    """Safe category; never raw response bodies or authorization headers."""


class DecisionProvider(Protocol):
    max_candidates: int
    max_state_bytes: int
    attempts: int
    billed_credits: int | None
    provider_request_id: str | None

    async def evaluate(self, state: dict, questions: dict) -> ProviderResponse: ...


def create_provider(settings, transport=None) -> DecisionProvider:
    if settings.aethras_decision_provider == "cloudflare_clef_flash":
        from app.decision_engine.cloudflare_clef_client import CloudflareClefClient
        return CloudflareClefClient(settings, transport)
    raise ProviderFailure("unsupported_provider")
