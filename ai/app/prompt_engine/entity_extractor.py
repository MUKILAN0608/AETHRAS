"""Entity extraction and world-state resolution."""

import re

from app.prompt_schemas import EntityReference

_ENTITY_PATTERNS: dict[str, re.Pattern] = {
    "ocean": re.compile(r"\b(ocean|sea|water|tide|river|lake)\b"),
    "fortress": re.compile(r"\b(fortress|castle|tower|keep|stronghold|citadel)\b"),
    "forest": re.compile(r"\b(forest|woods|grove|trees|woodland)\b"),
    "mountain": re.compile(r"\b(mountain|peak|summit|hill)\b"),
    "city": re.compile(r"\b(city|town|civilization|kingdom|ancient city)\b"),
    "storm": re.compile(r"\b(storm|storms|tempest|lightning)\b"),
    "moon": re.compile(r"\b(moon|invisible moon)\b"),
    "bridge": re.compile(r"\b(bridge)\b"),
    "walls": re.compile(r"\b(walls|wall)\b"),
    "foundation": re.compile(r"\b(foundation|foundations)\b"),
}


def extract_entity_names(normalized: str) -> list[str]:
    """Extract mentioned entity type names from prompt."""
    found: list[str] = []
    for name, pattern in _ENTITY_PATTERNS.items():
        if pattern.search(normalized):
            found.append(name)
    return found


def resolve_entities(
    names: list[str], world_context: dict
) -> list[EntityReference]:
    """Resolve entity names against compact world context."""
    entities_ctx = world_context.get("entities", {})
    nearby = world_context.get("nearby_entities", [])

    # Build lookup: type -> id
    type_to_ids: dict[str, list[str]] = {}
    for eid, edata in entities_ctx.items():
        etype = str(edata.get("type", "")).lower()
        type_to_ids.setdefault(etype, []).append(eid)
    for ent in nearby:
        etype = str(ent.get("type", "")).lower()
        eid = str(ent.get("id", ""))
        if eid:
            type_to_ids.setdefault(etype, []).append(eid)

    results: list[EntityReference] = []
    for name in names:
        ids = type_to_ids.get(name, [])
        if ids:
            results.append(
                EntityReference(
                    name=name.upper(),
                    entity_id=ids[0],
                    entity_type=name,
                    resolved=True,
                    resolution="FOUND",
                )
            )
        else:
            # moon is often not in world — ENTITY_NOT_FOUND
            resolution = "NOT_FOUND" if name in ("moon",) else "PROPOSED_CREATE"
            results.append(
                EntityReference(
                    name=name.upper(),
                    entity_id=None,
                    entity_type=name,
                    resolved=False,
                    resolution=resolution,
                )
            )
    return results
