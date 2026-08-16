"""Integration tests for full prompt pipeline."""

from app.prompt_engine.pipeline import pipeline
from app.prompt_schemas import InterpretRequest, ValidationStatus


def test_pipeline_flood():
    resp = pipeline.interpret(InterpretRequest(
        prompt="The ocean rises and consumes the fortress.",
        world_context={"entities": {"f1": {"type": "fortress"}, "o1": {"type": "ocean"}}},
    ))
    assert resp.status == ValidationStatus.VALID
    assert resp.action.action_type.value == "RAISE_WATER"
    assert resp.interpretation.original_prompt.startswith("The ocean")


def test_pipeline_fire():
    resp = pipeline.interpret(InterpretRequest(prompt="The forest catches fire."))
    assert resp.status == ValidationStatus.VALID
    assert resp.action.action_type.value == "START_FIRE"


def test_pipeline_memory_ambiguous_or_valid():
    resp = pipeline.interpret(InterpretRequest(
        prompt="The fortress remembers the last attack.",
        world_context={"entities": {"f1": {"type": "fortress"}}},
    ))
    assert resp.status in (ValidationStatus.VALID, ValidationStatus.AMBIGUOUS)
    assert resp.action.action_type.value == "MEMORY_ADD"


def test_pipeline_moon_invalid():
    resp = pipeline.interpret(InterpretRequest(prompt="The invisible moon destroys the ancient city."))
    assert resp.status == ValidationStatus.INVALID


def test_pipeline_contradiction_ambiguous():
    resp = pipeline.interpret(InterpretRequest(prompt="The mountain becomes the ocean, but remains a mountain."))
    assert resp.status == ValidationStatus.AMBIGUOUS


def test_pipeline_latency_recorded():
    resp = pipeline.interpret(InterpretRequest(prompt="The ocean rises."))
    assert resp.latency.total_ms >= 0
