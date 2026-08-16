"""Tests for action compilation."""

from app.prompt_engine.action_compiler import compile_action
from app.prompt_engine.constraint_extractor import extract_constraints
from app.prompt_engine.entity_extractor import extract_entity_names, resolve_entities
from app.prompt_engine.intent_detector import detect_intent
from app.prompt_engine.normalizer import normalize
from app.prompt_engine.strategic_analyzer import analyze_strategy
from app.prompt_schemas import ActionType, IntentType, SemanticInterpretation


def _interpret(prompt: str) -> SemanticInterpretation:
    original, normalized = normalize(prompt)
    names = extract_entity_names(normalized)
    return SemanticInterpretation(
        original_prompt=original,
        normalized_prompt=normalized,
        intent=detect_intent(normalized),
        entities=resolve_entities(names, {}),
        strategy=analyze_strategy(normalized, names),
        constraints=extract_constraints(normalized, names),
    )


def test_flood_action():
    action = compile_action(_interpret("The ocean rises and consumes the fortress."))
    assert action.action_type == ActionType.RAISE_WATER
    assert action.strategy == "ENVIRONMENTAL_ATTACK"


def test_fire_action():
    action = compile_action(_interpret("The forest catches fire."))
    assert action.action_type == ActionType.START_FIRE


def test_spatial_bypass():
    action = compile_action(_interpret("The storm enters the fortress without crossing its walls."))
    assert action.action_type == ActionType.SPATIAL_BYPASS


def test_indirect_structural():
    action = compile_action(_interpret("I don't destroy the fortress; I make the river destroy its foundation."))
    assert action.action_type == ActionType.INDIRECT_STRUCTURAL_ATTACK
