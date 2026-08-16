"""Action critic — identify unsupported entities, contradictions, missing targets."""

from app.prompt_schemas import ActionProposal, SemanticInterpretation


def critique(
    interpretation: SemanticInterpretation,
    action: ActionProposal | None,
) -> list[str]:
    """Return critic warnings (does not block pipeline)."""
    warnings: list[str] = []

    for e in interpretation.entities:
        if e.resolution == "NOT_FOUND":
            warnings.append(f"unsupported_entity:{e.name}")
        if e.resolution == "PROPOSED_CREATE" and e.name.lower() == "moon":
            warnings.append("hallucinated_entity:moon")

    if action is None:
        warnings.append("missing_action")
        return warnings

    if not action.target_entities:
        warnings.append("missing_target")

    if interpretation.intent.value == "CONTRADICTION":
        warnings.append("contradiction_detected")

    for c in interpretation.constraints:
        if c.constraint_type == "MUST_NOT_BE_DESTROYED":
            if action.action_type.value == "DESTROY_ENTITY":
                warnings.append("constraint_violation:must_not_destroy")

    return warnings
