"""Novelty scoring — compare action against history."""

from app.prompt_schemas import ActionProposal, ActionType


_KNOWN_PATTERNS: set[tuple[str, str]] = {
    ("RAISE_WATER", "FORTRESS"),
    ("START_FIRE", "FOREST"),
    ("MEMORY_ADD", "FORTRESS"),
    ("CREATE_STORM", "FORTRESS"),
}


def compute_novelty(
    action: ActionProposal | None,
    history: list[dict],
) -> float:
    """
    Compare current action against previous actions.

    Range 0.0 (repeated) → 1.0 (novel).
    """
    if action is None:
        return 0.0

    action_key = action.action_type.value
    target = action.target_entities[0] if action.target_entities else ""
    pattern = (action_key, target.upper())

    # Count repeats in history
    repeat_count = 0
    for entry in history:
        prev_action = entry.get("action_type") or entry.get("action", "")
        prev_target = entry.get("target", "")
        if prev_action == action_key and prev_target.upper() == target.upper():
            repeat_count += 1

    if repeat_count >= 2:
        return 0.12
    if repeat_count == 1:
        return 0.35
    if pattern in _KNOWN_PATTERNS and not history:
        return 0.71  # demo default for first flood
    if action.action_type in (
        ActionType.SPATIAL_BYPASS,
        ActionType.INDIRECT_STRUCTURAL_ATTACK,
        ActionType.CONTRADICTION_ATTACK,
    ):
        return 0.85
    if action.action_type == ActionType.MEMORY_ADD:
        return 0.62
    return 0.71
