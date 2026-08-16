"""Constraint extraction stage."""

import re

from app.prompt_schemas import Constraint

_NOT_DESTROY = re.compile(r"\b(don't destroy|do not destroy|without destroying|must not destroy)\b")
_WALLS_INTACT = re.compile(r"\b(without crossing|walls remain|without walls)\b")
_CONTRADICTION = re.compile(r"\b(but remains|but still|yet remains)\b")


def extract_constraints(normalized: str, entity_names: list[str]) -> list[Constraint]:
    """Extract explicit and implicit constraints."""
    constraints: list[Constraint] = []

    if _NOT_DESTROY.search(normalized):
        target = "FORTRESS" if "fortress" in entity_names else "TARGET"
        constraints.append(
            Constraint(
                constraint_type="MUST_NOT_BE_DESTROYED",
                entity=target,
                description=f"{target} must not be directly destroyed",
            )
        )
    if _WALLS_INTACT.search(normalized):
        constraints.append(
            Constraint(
                constraint_type="MUST_REMAIN_INTACT",
                entity="WALLS",
                description="Walls must remain intact",
            )
        )
        constraints.append(
            Constraint(
                constraint_type="MUST_ENTER",
                entity="STORM",
                description="Storm must enter fortress",
            )
        )
    if _CONTRADICTION.search(normalized):
        constraints.append(
            Constraint(
                constraint_type="CONFLICTING_TRANSFORMATION",
                entity="MOUNTAIN",
                description="Entity must become ocean AND remain mountain",
            )
        )
    return constraints
