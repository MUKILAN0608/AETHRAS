"""Tests for ambiguity detection."""

from app.prompt_engine.ambiguity import detect_ambiguity
from app.prompt_engine.action_compiler import compile_action
from app.prompt_engine.constraint_extractor import extract_constraints
from app.prompt_engine.entity_extractor import extract_entity_names, resolve_entities
from app.prompt_engine.intent_detector import detect_intent
from app.prompt_engine.normalizer import normalize
from app.prompt_engine.strategic_analyzer import analyze_strategy
from app.prompt_schemas import IntentType, SemanticInterpretation, ValidationStatus


def _full_interpret(prompt: str) -> tuple[SemanticInterpretation, object]:
    original, normalized = normalize(prompt)
    names = extract_entity_names(normalized)
    interp = SemanticInterpretation(
        original_prompt=original,
        normalized_prompt=normalized,
        intent=detect_intent(normalized),
        entities=resolve_entities(names, {}),
        strategy=analyze_strategy(normalized, names),
        constraints=extract_constraints(normalized, names),
    )
    action = compile_action(interp)
    return interp, action


def test_contradiction_ambiguous():
    interp, action = _full_interpret("The mountain becomes the ocean, but remains a mountain.")
    status, reasons, _ = detect_ambiguity(interp, action)
    assert status == ValidationStatus.AMBIGUOUS
    assert "CONFLICTING_TRANSFORMATION" in reasons[0]


def test_moon_invalid():
    interp, action = _full_interpret("The invisible moon destroys the ancient city.")
    status, reasons, _ = detect_ambiguity(interp, action)
    assert status == ValidationStatus.INVALID
