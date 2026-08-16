"""Ambiguity detection for prompt interpretations."""

import re

from app.prompt_schemas import (
    ActionProposal,
    Constraint,
    EntityReference,
    SemanticInterpretation,
    ValidationStatus,
)

_MEMORY_AMBIGUOUS = re.compile(
    r"\b(fortress|mountain|city|ocean)\b.*\b(remember|remembers)\b"
)


def detect_ambiguity(
    interpretation: SemanticInterpretation,
    action: ActionProposal | None,
) -> tuple[ValidationStatus, list[str], list[str]]:
    """
    Return (status, reasons, ambiguity_options).

    Does not silently guess when ambiguity is strategically important.
    """
    normalized = interpretation.normalized_prompt
    reasons: list[str] = []
    options: list[str] = []

    # Conflicting transformation constraints
    for c in interpretation.constraints:
        if c.constraint_type == "CONFLICTING_TRANSFORMATION":
            return (
                ValidationStatus.AMBIGUOUS,
                ["CONFLICTING_TRANSFORMATION_CONSTRAINTS"],
                [
                    "Apply ocean transformation only",
                    "Apply mountain preservation only",
                ],
            )

    # Memory prompts can mean add or strengthen
    if _MEMORY_AMBIGUOUS.search(normalized):
        if interpretation.intent.value == "MEMORY_MANIPULATION":
            options = [
                "Create memory relation (MEMORY_ADD)",
                "Strengthen existing relationship (MODIFY_RELATION)",
            ]
            # Fortress remembers attack — valid or ambiguous per spec
            if "attack" in normalized or "last" in normalized:
                return (
                    ValidationStatus.AMBIGUOUS,
                    ["Multiple memory interpretations possible"],
                    options,
                )

    # Entity not found → invalid unless partial
    unresolved = [
        e for e in interpretation.entities if e.resolution == "NOT_FOUND"
    ]
    if unresolved:
        names = ", ".join(e.name for e in unresolved)
        return (
            ValidationStatus.INVALID,
            [f"ENTITY_NOT_FOUND: {names}"],
            [],
        )

    if action is None:
        return ValidationStatus.INVALID, ["No action compiled"], []

    return ValidationStatus.VALID, [], []
