"""Tests for action validator."""

from app.prompt_engine.action_validator import validate_action
from app.prompt_schemas import ActionProposal, ActionType, ValidationStatus


def test_invalid_moon():
    action = ActionProposal(
        action_id="act_test",
        action_type=ActionType.DESTROY_ENTITY,
        target_entities=["moon"],
        parameters={"intensity": 0.8},
        confidence=0.2,
    )
    result = validate_action(action, {})
    assert result.status == ValidationStatus.INVALID


def test_valid_flood():
    action = ActionProposal(
        action_id="act_test",
        action_type=ActionType.RAISE_WATER,
        target_entities=["fortress"],
        parameters={"intensity": 0.87},
        confidence=0.94,
    )
    result = validate_action(action, {"entities": {"f1": {"type": "fortress"}}})
    assert result.status == ValidationStatus.VALID
