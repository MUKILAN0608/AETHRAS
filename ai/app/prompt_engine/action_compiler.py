"""Semantic action compiler — interpretation → ActionProposal."""

import uuid

import re

from app.prompt_schemas import (
    ActionProposal,
    ActionType,
    Constraint,
    EntityReference,
    IntentType,
    SemanticInterpretation,
)

_FLOOD = re.compile(r"\b(ocean|water|flood|rise|consumes|consume|submerge)\b")
_FIRE = re.compile(r"\b(fire|burn|burns|burning|catches fire|catch fire|ignite)\b")
_MEMORY = re.compile(r"\b(remember|remembers|recall|memory)\b")
_STORM = re.compile(r"\b(storm|storms|tempest|lightning)\b")
_SPATIAL = re.compile(r"\b(without crossing|bypass|enters without|without walls)\b")
_INDIRECT = re.compile(r"\b(don't destroy|do not destroy|without destroying|foundation)\b")
_DESTROY = re.compile(r"\b(destroy|destroys|demolish|consume|consumes)\b")
_CONTRADICTION = re.compile(r"\b(but remains|but still|yet remains)\b")


def _entity_id(entities: list[EntityReference], name: str) -> str | None:
    name_lower = name.lower()
    for e in entities:
        if e.name.lower() == name_lower or (e.entity_type and e.entity_type.lower() == name_lower):
            return e.entity_id
    return None


def _entity_ids(entities: list[EntityReference], *names: str) -> list[str]:
    ids: list[str] = []
    for n in names:
        eid = _entity_id(entities, n)
        if eid:
            ids.append(eid)
    return ids


def compile_action(interpretation: SemanticInterpretation) -> ActionProposal | None:
    """Compile semantic interpretation into a canonical action proposal."""
    norm = interpretation.normalized_prompt
    entities = interpretation.entities
    strategy = interpretation.strategy
    constraints = interpretation.constraints

    action_type = ActionType.NONE
    source_ids: list[str] = []
    target_ids: list[str] = []
    intensity = 0.8
    strategy_label = strategy.strategy_type if strategy else ""

    if _CONTRADICTION.search(norm):
        action_type = ActionType.CONTRADICTION_ATTACK
        target_ids = _entity_ids(entities, "mountain") or ["mountain"]
        intensity = 0.5
    elif _INDIRECT.search(norm):
        action_type = ActionType.INDIRECT_STRUCTURAL_ATTACK
        target_ids = _entity_ids(entities, "fortress", "foundation") or ["fortress"]
        source_ids = _entity_ids(entities, "river") or []
        intensity = 0.86
        strategy_label = "INDIRECT_STRUCTURAL_ATTACK"
    elif _SPATIAL.search(norm) and _STORM.search(norm):
        action_type = ActionType.SPATIAL_BYPASS
        target_ids = _entity_ids(entities, "fortress") or ["fortress"]
        source_ids = _entity_ids(entities, "storm") or []
        intensity = 0.82
        strategy_label = "SPATIAL_BYPASS"
    elif _FIRE.search(norm):
        action_type = ActionType.START_FIRE
        target_ids = _entity_ids(entities, "forest") or ["forest"]
        intensity = 0.85
        strategy_label = "ENVIRONMENTAL_ATTACK"
    elif _FLOOD.search(norm) or (
        interpretation.intent == IntentType.ENVIRONMENTAL_TRANSFORMATION
        and _DESTROY.search(norm)
    ):
        action_type = ActionType.RAISE_WATER
        source_ids = _entity_ids(entities, "ocean") or []
        target_ids = _entity_ids(entities, "fortress", "city") or ["fortress"]
        intensity = 0.87 if "fortress" in norm else 0.8
        strategy_label = "ENVIRONMENTAL_ATTACK"
    elif _MEMORY.search(norm):
        action_type = ActionType.MEMORY_ADD
        target_ids = _entity_ids(entities, "fortress", "mountain", "city", "ocean") or ["fortress"]
        intensity = 0.75
        strategy_label = "MEMORY_ATTACK"
    elif _STORM.search(norm):
        action_type = ActionType.CREATE_STORM
        target_ids = _entity_ids(entities, "fortress", "city") or ["world"]
        intensity = 0.7
    elif interpretation.intent == IntentType.ENTITY_DESTRUCTION:
        action_type = ActionType.DESTROY_ENTITY
        target_ids = [e.entity_id for e in entities if e.entity_id and e.resolved]
        if not target_ids:
            target_ids = [entities[-1].name.lower()] if entities else []
        intensity = 0.8

    if action_type == ActionType.NONE:
        return None

    # Block actions targeting unresolved NOT_FOUND entities
    for e in entities:
        if e.resolution == "NOT_FOUND":
            return ActionProposal(
                action_id=f"act_{uuid.uuid4().hex[:8]}",
                action_type=ActionType.DESTROY_ENTITY if _DESTROY.search(norm) else ActionType.NONE,
                source_entities=source_ids,
                target_entities=[e.name.lower()],
                parameters={"intensity": intensity},
                strategy=strategy_label,
                constraints=constraints,
                confidence=0.2,
                novelty=0.0,
            )

    conf = 0.94 if action_type == ActionType.RAISE_WATER else 0.88
    if action_type == ActionType.START_FIRE:
        conf = 0.91
    if action_type == ActionType.SPATIAL_BYPASS:
        conf = 0.82
    if action_type == ActionType.INDIRECT_STRUCTURAL_ATTACK:
        conf = 0.86
    if action_type == ActionType.MEMORY_ADD:
        conf = 0.78
    if action_type == ActionType.CONTRADICTION_ATTACK:
        conf = 0.55

    return ActionProposal(
        action_id=f"act_{uuid.uuid4().hex[:8]}",
        action_type=action_type,
        actor="human",
        source_entities=source_ids,
        target_entities=target_ids if target_ids else [e.entity_id or e.name.lower() for e in entities[-1:]],
        parameters={"intensity": intensity, "magnitude": intensity},
        strategy=strategy_label,
        constraints=constraints,
        confidence=conf,
        novelty=0.0,
    )
