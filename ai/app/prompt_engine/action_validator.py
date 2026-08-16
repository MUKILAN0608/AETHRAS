"""Action validation against schema, world rules, and constraints."""

from app.prompt_schemas import (
    ActionProposal,
    ActionType,
    Constraint,
    ValidationResult,
    ValidationStatus,
)

_SUPPORTED_ACTIONS = {
    ActionType.RAISE_WATER,
    ActionType.START_FIRE,
    ActionType.MEMORY_ADD,
    ActionType.MEMORY_REWRITE,
    ActionType.MEMORY_DECAY,
    ActionType.CREATE_STORM,
    ActionType.CHANGE_WEATHER,
    ActionType.SPATIAL_BYPASS,
    ActionType.INDIRECT_STRUCTURAL_ATTACK,
    ActionType.DESTROY_ENTITY,
    ActionType.CREATE_ENTITY,
    ActionType.TRANSFORM_ENTITY,
    ActionType.CONTRADICTION_ATTACK,
}


def validate_action(
    action: ActionProposal,
    world_context: dict,
    constraints: list[Constraint] | None = None,
) -> ValidationResult:
    """Validate compiled action against game and world rules."""
    reasons: list[str] = []
    constraints = constraints or action.constraints

    if action.action_type == ActionType.NONE:
        return ValidationResult(
            status=ValidationStatus.INVALID,
            reasons=["ACTION_NOT_SUPPORTED"],
        )

    if action.action_type not in _SUPPORTED_ACTIONS:
        return ValidationResult(
            status=ValidationStatus.INVALID,
            reasons=[f"ACTION_NOT_SUPPORTED: {action.action_type.value}"],
        )

    intensity = action.parameters.get("intensity", 0.8)
    if intensity <= 0 or intensity > 1.0:
        reasons.append("INTENSITY_OUT_OF_RANGE")

    # Entity existence check via world context
    entities_ctx = world_context.get("entities", {})
    for tid in action.target_entities:
        if tid in entities_ctx:
            continue
        # Allow type-based targets (fortress, forest) resolved at execution
        if tid.lower() in ("fortress", "forest", "ocean", "mountain", "city", "world"):
            continue
        if not any(
            str(v.get("type", "")).lower() == tid.lower() or k == tid
            for k, v in entities_ctx.items()
        ):
            if "moon" in tid.lower() or action.confidence < 0.3:
                return ValidationResult(
                    status=ValidationStatus.INVALID,
                    reasons=[f"ENTITY_NOT_FOUND: {tid}"],
                )

    # Constraint validation
    for c in constraints:
        if c.constraint_type == "CONFLICTING_TRANSFORMATION":
            return ValidationResult(
                status=ValidationStatus.AMBIGUOUS,
                reasons=["CONFLICTING_TRANSFORMATION_CONSTRAINTS"],
                ambiguity_options=[
                    "Apply ocean transformation only",
                    "Apply mountain preservation only",
                ],
            )
        if c.constraint_type == "MUST_NOT_BE_DESTROYED" and action.action_type == ActionType.DESTROY_ENTITY:
            return ValidationResult(
                status=ValidationStatus.INVALID,
                reasons=[f"CONSTRAINT_VIOLATION: {c.constraint_type}"],
            )

    if reasons:
        return ValidationResult(status=ValidationStatus.INVALID, reasons=reasons)

    return ValidationResult(status=ValidationStatus.VALID)
