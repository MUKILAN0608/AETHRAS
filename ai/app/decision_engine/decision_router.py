import json
import math
import time
import uuid

from app.decision_engine.provider import create_provider, ProviderFailure
from app.decision_engine.questions import IMPACT_LEVELS, questions_for
from app.decision_engine.schemas import DecisionResult


async def evaluate_decision(state, candidate_actions, settings, transport=None, *, provider=None):
    """Stable vendor-independent result; caller retains critic and validation authority."""
    ids = [action.action_id for action in candidate_actions]
    result = DecisionResult(request_id=uuid.uuid4().hex, candidate_ids=ids,
                            provider=settings.aethras_decision_provider,
                            model=settings.decision_model)
    if not settings.aethras_decision_enabled:
        return result
    if not ids:
        result.status = "skipped"
        result.reason = "no_candidate"
        return result
    started = time.perf_counter()
    client = provider or create_provider(settings, transport)
    try:
        if len(ids) > client.max_candidates or len(set(ids)) != len(ids) or "none_of_the_above" in ids:
            raise ProviderFailure("invalid_candidates")
        state = {**state, "candidates": [a.model_dump(mode="json") for a in candidate_actions]}
        if len(json.dumps(state, ensure_ascii=False).encode()) > client.max_state_bytes:
            raise ProviderFailure("state_too_large")
        questions = questions_for(ids)
        result.invoked = True
        response = await client.evaluate(state, questions)
        result.resolved_model = response.model
        result.usage = response.usage.model_dump()
        answers = response.answers
        if set(answers) != set(questions):
            raise ProviderFailure("unexpected_answers")
        for key, question in questions.items():
            answer = answers[key]
            if answer.type != question["type"]:
                raise ProviderFailure("unexpected_answer_type")
            if answer.type in ("choice", "score"):
                expected = set(question["criteria"]) if answer.type == "choice" else {"0", "1", "2"}
                if set(answer.probabilities) != expected or not math.isclose(sum(answer.probabilities.values()), 1, abs_tol=0.001):
                    raise ProviderFailure("invalid_distribution")
                if answer.type == "choice":
                    if answer.choice not in expected or answer.probabilities[answer.choice] < max(answer.probabilities.values()):
                        raise ProviderFailure("invalid_choice")
                elif answer.legend != {str(i): v for i, v in enumerate(IMPACT_LEVELS)}:
                    raise ProviderFailure("invalid_legend")
                elif not math.isclose(answer.score, sum(int(i) * p for i, p in answer.probabilities.items()), abs_tol=0.02):
                    raise ProviderFailure("inconsistent_score")
                result.probabilities[key] = answer.probabilities
        impact = answers["strategic_impact"]
        result.strategic_impact = impact.score
        result.confidence = impact.confidence
        result.review_probability = answers["review"].noul
        result.simulation_probability = answers["simulation"].noul
        result.selected_candidate = ids[0]
        selection_ambiguous = False
        if "selection" in answers:
            selection = answers["selection"]
            result.confidence = min(result.confidence, selection.confidence)
            result.selected_candidate = selection.choice if selection.choice in ids else None
            ranked = sorted(selection.probabilities.values(), reverse=True)
            selection_ambiguous = ranked[0] - ranked[1] <= settings.decision_selection_min_margin
        result.review_required = (
            result.selected_candidate is None or selection_ambiguous or result.confidence < settings.decision_min_confidence
            or result.review_probability >= settings.decision_review_threshold
        )
        result.simulation_recommended = result.simulation_probability >= settings.decision_simulation_threshold
        result.status = "review" if result.review_required else "evaluated"
    except ProviderFailure as error:
        result.status = "fallback"
        result.fallback = True
        result.review_required = True
        result.selected_candidate = None
        result.reason = str(error)
    finally:
        result.attempts = client.attempts
        result.billed_credits = client.billed_credits
        result.provider_request_id = client.provider_request_id
        result.billing_status = "reported" if client.billed_credits is not None else "not_reported"
        result.latency_ms = round((time.perf_counter() - started) * 1000, 2)
    return result
