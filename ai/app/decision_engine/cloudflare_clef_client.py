"""Workers AI REST envelope around the documented Clef-Flash output schema."""
import asyncio
import math
import random
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import httpx
from pydantic import BaseModel, Field, StrictBool, ValidationError

from app.decision_engine.provider import ProviderFailure
from app.decision_engine.schemas import ProviderResponse


class CloudflareEnvelope(BaseModel):
    success: StrictBool
    errors: list[dict] = Field(default_factory=list)
    messages: list = Field(default_factory=list)
    result: ProviderResponse | None = None


def retry_delay(header, attempt):
    delay = 0.25 * 2 ** attempt
    if header:
        try:
            value = float(header)
        except ValueError:
            try:
                value = (parsedate_to_datetime(header) - datetime.now(timezone.utc)).total_seconds()
            except (ValueError, TypeError, OverflowError):
                value = delay
        if math.isfinite(value) and value >= 0:
            delay = max(delay, value)
    return delay + random.uniform(0, 0.25)


class CloudflareClefClient:
    max_candidates = 254  # Plus none_of_the_above: documented 255-option maximum.
    max_state_bytes = 24000  # Conservative local budget, not exact token counting.

    def __init__(self, settings, transport=None):
        self.settings = settings
        self.transport = transport
        self.attempts = 0
        self.billed_credits = None  # No documented per-request billed-credit header.
        self.provider_request_id = None

    async def evaluate(self, state, questions):
        cfg = self.settings
        try:
            async with asyncio.timeout(cfg.aethras_decision_timeout_seconds):
                timeout = httpx.Timeout(cfg.aethras_decision_timeout_seconds,
                                        connect=min(1.0, cfg.aethras_decision_timeout_seconds))
                async with httpx.AsyncClient(transport=self.transport, timeout=timeout,
                                            follow_redirects=False) as client:
                    for attempt in range(cfg.aethras_decision_max_retries + 1):
                        self.attempts += 1
                        async with client.stream(
                            "POST", cfg.decision_api_url,
                            headers={"Authorization": f"Bearer {cfg.cloudflare_auth_token.get_secret_value()}"},
                            json={"model": "clef-flash", "state": state, "questions": questions},
                        ) as response:
                            ray = response.headers.get("cf-ray")
                            if ray and len(ray) <= 128 and all(c.isalnum() or c == '-' for c in ray):
                                self.provider_request_id = ray
                            if response.status_code in (429, 502, 503, 504) and attempt < cfg.aethras_decision_max_retries:
                                delay = retry_delay(response.headers.get("retry-after"), attempt)
                            else:
                                if response.status_code != 200:
                                    raise ProviderFailure(f"http_{response.status_code}")
                                body = bytearray()
                                async for chunk in response.aiter_bytes():
                                    body.extend(chunk)
                                    if len(body) > 262144:
                                        raise ProviderFailure("response_too_large")
                                try:
                                    envelope = CloudflareEnvelope.model_validate_json(body)
                                except (ValidationError, ValueError, TypeError):
                                    raise ProviderFailure("malformed_response") from None
                                if not envelope.success or envelope.errors:
                                    raise ProviderFailure("cloudflare_error")
                                if envelope.result is None:
                                    raise ProviderFailure("missing_result")
                                return envelope.result
                        await asyncio.sleep(delay)
        except (TimeoutError, httpx.TimeoutException):
            raise ProviderFailure("timeout") from None
        except httpx.RequestError:
            # Never retry uncertain delivery; the first request may have succeeded.
            raise ProviderFailure("network_error") from None
