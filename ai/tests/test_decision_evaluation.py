"""Offline checks of study pairing and metering; these are synthetic Go replies."""
import importlib.util
from pathlib import Path

import httpx
import pytest


def harness():
    path = Path(__file__).resolve().parents[2] / "scripts" / "evaluate-decisions.py"
    spec = importlib.util.spec_from_file_location("decision_evaluation", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_study_distinguishes_billed_credits_from_token_estimates():
    module = harness()
    calls = []
    def handler(request):
        if request.url.path == "/api/world/generate":
            return httpx.Response(200, json={})
        calls.append(request.url.path)
        return httpx.Response(200, json={"status": "VALID", "action": {"action_id": "fixture", "action_type": "RAISE_WATER"},
            "decision": {"provider": "cloudflare_clef_flash", "status": "evaluated", "invoked": True,
                         "candidate_ids": ["fixture"], "usage": {"input_tokens": 100, "output_tokens": 0},
                         "billed_credits": 3 if len(calls) % 2 else None}})
    metrics = module.study("https://offline.invalid", True, 1, 1, httpx.MockTransport(handler))["metrics"]
    assert metrics["actual_billed_credits_reported"] == 6
    assert metrics["input_tokens"] == 400
    assert metrics["unmetered_requests"] == 2
    assert metrics["invalid_selection_rate"] is None


def test_pairing_rejects_changed_candidates_but_allows_different_ids():
    module = harness()
    first = {"records": [{"seed": 42, "prompt": "p", "action": {"action_id": "first", "action_type": "RAISE_WATER"}}]}
    second = {"records": [{"seed": 42, "prompt": "p", "action": {"action_id": "second", "action_type": "RAISE_WATER"}}]}
    module.assert_paired_candidates(first, second)
    second["records"][0]["action"]["action_type"] = "START_FIRE"
    with pytest.raises(RuntimeError, match="same seeded candidate"):
        module.assert_paired_candidates(first, second)
