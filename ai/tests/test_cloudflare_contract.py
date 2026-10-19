"""Synthetic Workers AI responses, not observations of live inference."""
import asyncio
import json

import httpx
import pytest
from fastapi.testclient import TestClient

from app.decision_engine.cloudflare_clef_client import CloudflareClefClient
from app.decision_engine.decision_router import evaluate_decision
from tests.test_decision_engine import candidates, config, envelope, fixture, run


@pytest.mark.parametrize("payload,reason", [
    ({"success": False, "errors": [{"code": 10000, "message": "private provider error"}], "result": None}, "cloudflare_error"),
    ({"success": True, "errors": [{"code": 1}]}, "cloudflare_error"),
    ({"success": True, "errors": [], "result": None}, "missing_result"),
    ({"success": "true", "result": None}, "malformed_response"),
    ({"answers": {}}, "malformed_response"),
])
def test_cloudflare_envelope_failure(payload, reason):
    result = run(handler=lambda r: httpx.Response(200, json=payload))
    assert result.reason == reason and result.review_required
    assert "private provider error" not in result.model_dump_json()


def test_cf_ray_is_recorded_without_raw_provider_headers():
    result = run(handler=lambda r: httpx.Response(200, json=envelope(fixture()), headers={"cf-ray": "abc123-BOM", "x-credits-charged": "999", "authorization": "secret"}))
    assert result.provider_request_id == "abc123-BOM"
    assert result.billed_credits is None and result.billing_status == "not_reported"
    assert "secret" not in result.model_dump_json()


def test_output_usage_follows_schema_without_assuming_zero():
    data = fixture()
    data["usage"]["output_tokens"] = 12
    assert run(data).usage["output_tokens"] == 12


def test_documented_candidate_limit():
    result = run(count=255)
    assert result.reason == "invalid_candidates" and not result.invoked


def test_cloudflare_request_auth_and_no_other_provider():
    def handler(request):
        body = json.loads(request.content)
        assert body["model"] == "clef-flash"
        assert request.url.path.endswith("/ai/run/@cf/cloudflare/clef-flash")
        assert body["state"]["candidates"][0]["action_id"] == "a0"
        assert request.headers["authorization"] == "Bearer test-only-key"
        return httpx.Response(200, json=envelope(fixture()))
    result = run(handler=handler)
    assert result.status == "evaluated" and result.provider == "cloudflare_clef_flash"


def test_real_endpoint_uses_mocked_cloudflare_transport(monkeypatch):
    from app import main, research_logger
    from app.decision_engine import decision_router
    monkeypatch.setattr(main, "settings", config())
    transport = httpx.MockTransport(lambda r: httpx.Response(200, json=envelope(fixture())))
    monkeypatch.setattr(decision_router, "create_provider", lambda settings, unused: CloudflareClefClient(settings, transport))
    response = TestClient(main.app).post("/api/v1/prompt/interpret", json={
        "prompt": "The ocean rises and consumes the fortress.",
        "world_context": {"entities": {"o1": {"type": "ocean"}, "f1": {"type": "fortress"}}}})
    assert response.status_code == 200 and response.json()["status"] == "VALID"
    assert response.json()["decision"]["provider"] == "cloudflare_clef_flash"
    records = research_logger._LOG_FILE.read_text(encoding="utf-8")
    event = json.loads(records.splitlines()[-1])
    assert event["decision"]["version"] == "decision-v3" and "critic_findings" in event
    assert "test-only-key" not in records


def test_health_does_not_disclose_account_or_token(monkeypatch):
    from app import main
    monkeypatch.setattr(main, "settings", config())
    data = TestClient(main.app).get("/api/v1/prompt/health")
    assert data.json()["decision_engine"]["configured"]
    assert "test-only-key" not in data.text and "a" * 32 not in data.text
