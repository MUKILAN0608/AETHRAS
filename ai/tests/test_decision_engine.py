"""Offline contract/policy tests. All provider responses below are synthetic fixtures."""
import asyncio
import os

import httpx
import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.decision_engine.decision_router import evaluate_decision
from app.decision_engine.questions import IMPACT_LEVELS
from app.prompt_schemas import ActionProposal, ActionType


def config(**kwargs):
    return Settings(_env_file=None, aethras_decision_enabled=True, cloudflare_account_id="a" * 32, cloudflare_auth_token="test-only-key", **kwargs)


def candidates(count=1):
    return [ActionProposal(action_id=f"a{i}", action_type=ActionType.RAISE_WATER) for i in range(count)]


def fixture(selection=False):
    data = {"model": "fixture-model", "answers": {
        "strategic_impact": {"type": "score", "score": 1.0,
                             "legend": {str(i): v for i, v in enumerate(IMPACT_LEVELS)},
                             "probabilities": {"0": 0.0, "1": 1.0, "2": 0.0}, "confidence": 0.9},
        "review": {"type": "noul", "noul": 0.1},
        "simulation": {"type": "noul", "noul": 0.8},
    }, "usage": {"input_tokens": 100, "output_tokens": 0}}
    if selection:
        data["answers"]["selection"] = {"type": "choice", "choice": "a1", "confidence": 0.9,
            "probabilities": {"a0": 0.1, "a1": 0.8, "none_of_the_above": 0.1}}
    return data


def envelope(result):
    return {"success": True, "errors": [], "messages": [], "result": result}


def run(data=None, count=1, handler=None, **kwargs):
    transport = httpx.MockTransport(handler or (lambda r: httpx.Response(200, json=envelope(data or fixture()))))
    return asyncio.run(evaluate_decision({"prompt": "ocean rises"}, candidates(count), config(**kwargs), transport))


def test_single_candidate_routing_and_batch_request():
    def handler(request):
        import json
        payload = json.loads(request.content)
        assert set(payload) == {"model", "state", "questions"}
        assert payload["model"] == "clef-flash"
        assert str(request.url) == f"https://api.cloudflare.com/client/v4/accounts/{'a' * 32}/ai/run/@cf/cloudflare/clef-flash"
        assert set(payload["questions"]) == {"strategic_impact", "review", "simulation"}
        assert request.headers["Authorization"] == "Bearer test-only-key"
        return httpx.Response(200, json=envelope(fixture()))
    result = run(handler=handler)
    assert result.status == "evaluated" and result.selected_candidate == "a0"
    assert result.simulation_recommended and not result.review_required
    assert result.usage["input_tokens"] == 100


def test_multiple_candidate_selection():
    result = run(fixture(True), 2)
    assert result.selected_candidate == "a1"


def test_tied_selection_requires_review_even_with_high_confidence():
    data = fixture(True)
    data["answers"]["selection"]["probabilities"] = {"a0": 0.5, "a1": 0.5, "none_of_the_above": 0.0}
    assert run(data, 2).review_required


@pytest.mark.parametrize("mutation", ["unknown_choice", "missing", "wrong_type", "nan", "distribution", "legend", "score", "extra"])
def test_malformed_responses_fail_closed(mutation):
    data = fixture(True)
    answers = data["answers"]
    if mutation == "unknown_choice": answers["selection"]["choice"] = "invented"
    if mutation == "missing": del answers["review"]
    if mutation == "wrong_type": answers["review"] = {"type": "choice"}
    if mutation == "nan": answers["review"]["noul"] = "NaN"
    if mutation == "distribution": answers["selection"]["probabilities"]["a1"] = 0.1
    if mutation == "legend": answers["strategic_impact"]["legend"]["0"] = "changed"
    if mutation == "score": answers["strategic_impact"]["score"] = 2.0
    if mutation == "extra": answers["surprise"] = {"type": "noul", "noul": 0.0}
    result = run(data, 2)
    assert result.fallback and result.review_required and result.selected_candidate is None


def test_none_of_the_above():
    data = fixture(True)
    data["answers"]["selection"].update(choice="none_of_the_above", probabilities={"a0": 0.0, "a1": 0.0, "none_of_the_above": 1.0})
    result = run(data, 2)
    assert result.review_required and result.selected_candidate is None and not result.fallback


def test_low_confidence_and_review_threshold():
    data = fixture()
    data["answers"]["strategic_impact"]["confidence"] = 0.2
    assert run(data).review_required
    data = fixture()
    data["answers"]["review"]["noul"] = 0.5
    assert run(data).review_required


@pytest.mark.parametrize("status", [401, 403, 422, 429, 500, 502, 503, 504])
def test_http_failure_no_default_retries(status):
    result = run(handler=lambda r: httpx.Response(status, text="secret provider error"))
    assert result.reason == f"http_{status}" and result.attempts == 1 and result.review_required
    assert "secret" not in result.model_dump_json()


@pytest.mark.parametrize("error", [httpx.ConnectError, httpx.ReadTimeout])
def test_network_errors(error):
    def handler(request): raise error("private details", request=request)
    result = run(handler=handler, aethras_decision_max_retries=2)
    assert result.review_required and result.attempts == 1


def test_retry_only_explicit_rate_limit():
    calls = []
    def handler(request):
        calls.append(request.content)
        return httpx.Response(429) if len(calls) == 1 else httpx.Response(200, json=envelope(fixture()))
    result = run(handler=handler, aethras_decision_max_retries=1)
    assert result.attempts == 2 and calls[0] == calls[1] and not result.fallback


def test_total_deadline():
    async def handler(request):
        await asyncio.sleep(0.1)
        return httpx.Response(200, json=envelope(fixture()))
    result = run(handler=handler, aethras_decision_timeout_seconds=0.01)
    assert result.reason == "timeout"


def test_disabled_and_no_candidates_do_not_call():
    def handler(r): pytest.fail("unexpected HTTP")
    transport = httpx.MockTransport(handler)
    disabled = Settings(_env_file=None, aethras_decision_enabled=False)
    assert asyncio.run(evaluate_decision({}, candidates(), disabled, transport)).status == "disabled"
    assert asyncio.run(evaluate_decision({}, [], config(), transport)).status == "skipped"


def test_invalid_configuration():
    with pytest.raises(ValueError): Settings(_env_file=None, aethras_decision_enabled=True, cloudflare_auth_token="")
    with pytest.raises(ValueError): config(cloudflare_clef_api_base_url="http://example.com")
    with pytest.raises(ValueError): config(cloudflare_clef_model="unsupported")
    with pytest.raises(ValueError): config(aethras_decision_provider="unsupported")














def test_service_unavailable_retries_within_budget():
    calls = []
    def handler(request):
        calls.append(request.content)
        return httpx.Response(503, headers={"Retry-After": "0"}) if len(calls) == 1 else httpx.Response(200, json=envelope(fixture()))
    result = run(handler=handler, aethras_decision_max_retries=1)
    assert result.attempts == 2 and not result.fallback


def test_retry_after_beyond_deadline_never_calls_again():
    result = run(handler=lambda r: httpx.Response(429, headers={"Retry-After": "60"}), aethras_decision_max_retries=2, aethras_decision_timeout_seconds=0.02)
    assert result.reason == "timeout" and result.attempts == 1


def test_unknown_delivery_never_reports_zero_billing():
    def handler(request): raise httpx.ReadTimeout("private details", request=request)
    result = run(handler=handler)
    assert result.billed_credits is None and result.billing_status == "not_reported"


def test_provider_can_be_injected_without_vendor_coupling():
    from app.decision_engine.schemas import ProviderResponse
    class FakeProvider:
        max_candidates = 10
        max_state_bytes = 5000
        attempts = 0
        billed_credits = None
        provider_request_id = "fake"
        async def evaluate(self, state, questions):
            self.attempts += 1
            return ProviderResponse.model_validate(fixture())
    result = asyncio.run(evaluate_decision({}, candidates(), config(), provider=FakeProvider()))
    assert result.status == "evaluated" and result.attempts == 1


def test_state_bound():
    result = asyncio.run(evaluate_decision({"prompt": "x" * 25000}, candidates(), config()))
    assert result.reason == "state_too_large" and not result.invoked and result.review_required


def test_critic_cannot_be_upgraded(monkeypatch):
    from app import main
    from app.decision_engine.schemas import DecisionResult
    async def fake(state, candidates, settings):
        assert not candidates
        return DecisionResult(request_id="fixture", status="skipped")
    monkeypatch.setattr(main, "evaluate_decision", fake)
    response = TestClient(main.app).post("/api/v1/prompt/interpret", json={"prompt": "The invisible moon destroys the ancient city."})
    assert response.status_code == 200 and response.json()["status"] == "INVALID"


def test_policy_downgrades_valid_pipeline(monkeypatch):
    from app import main
    from app.decision_engine.schemas import DecisionResult
    async def fake(state, candidates, settings):
        assert len(candidates) == 1
        return DecisionResult(request_id="fixture", status="fallback", review_required=True, fallback=True)
    monkeypatch.setattr(main, "evaluate_decision", fake)
    response = TestClient(main.app).post("/api/v1/prompt/interpret", json={"prompt": "The ocean rises."})
    assert response.json()["status"] == "AMBIGUOUS"
    assert response.json()["validation"]["status"] == "AMBIGUOUS"




@pytest.mark.skipif(os.getenv("AETHRAS_DECISION_LIVE_TEST", "").lower() != "true", reason="Explicit live opt-in and key required")
def test_live_smoke():
    settings = Settings(aethras_decision_enabled=True)
    result = asyncio.run(evaluate_decision({"prompt": "The ocean rises", "world": {"entities": []}}, candidates(), settings))
    assert result.invoked and not result.fallback, result.reason
    assert result.resolved_model and result.usage["output_tokens"] >= 0
    assert result.provider == "cloudflare_clef_flash"
