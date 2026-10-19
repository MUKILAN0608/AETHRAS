"""Test-only ASGI app: a delayed HTTP mock exercises timeout/UI recovery offline.

Never use this app as the production entrypoint. Research records go to the
smoke harness's temporary directory, and no hosted request is made.
"""
import asyncio
import os
from pathlib import Path

import httpx

from app import main, research_logger
from app.config import Settings
from app.decision_engine import decision_router
from app.decision_engine.cloudflare_clef_client import CloudflareClefClient

log_directory = os.environ.get("AETHRAS_TEST_LOG_DIR")
if not log_directory:
    raise RuntimeError("The test-only ASGI app requires an isolated test log directory")
research_logger._LOG_DIR = Path(log_directory)
research_logger._LOG_FILE = Path(log_directory) / "experiments.jsonl"
main.settings = Settings(_env_file=None, aethras_decision_enabled=True,
                         cloudflare_account_id="a" * 32, cloudflare_auth_token="offline-test-only",
                         aethras_decision_timeout_seconds=0.3)


async def delayed_response(request):
    await asyncio.sleep(1)
    raise AssertionError("The overall deadline should cancel this mock before completion")


transport = httpx.MockTransport(delayed_response)
decision_router.create_provider = lambda settings, unused=None: CloudflareClefClient(settings, transport)
app = main.app
