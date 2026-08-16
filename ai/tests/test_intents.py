"""Tests for intent detection."""

from app.prompt_engine.intent_detector import detect_intent
from app.prompt_schemas import IntentType


def test_flood_intent():
    assert detect_intent("the ocean rises and consumes the fortress.") == IntentType.ENVIRONMENTAL_TRANSFORMATION


def test_memory_intent():
    assert detect_intent("the fortress remembers the last attack.") == IntentType.MEMORY_MANIPULATION


def test_spatial_intent():
    assert detect_intent("the storm enters the fortress without crossing its walls.") == IntentType.SPATIAL_ATTACK


def test_contradiction_intent():
    assert detect_intent("the mountain becomes the ocean, but remains a mountain.") == IntentType.CONTRADICTION
