"""Compact world context builder for LLM inference."""

from typing import Any


def build_world_context(
    full_state: dict[str, Any],
    prompt: str = "",
    turn: int = 1,
) -> dict[str, Any]:
    """
    Extract only relevant state for prompt interpretation.

    Do not send the entire world database.
    """
    entities = full_state.get("entities", {})
    relationships = full_state.get("relationships", [])
    env = full_state.get("environmental_state", {})

    # Keywords from prompt for relevance filtering
    prompt_lower = prompt.lower()
    relevant_types = {
        "fortress", "forest", "ocean", "mountain", "city", "storm", "river", "moon"
    }
    mentioned = {t for t in relevant_types if t in prompt_lower}

    nearby: list[dict] = []
    target_entities: list[dict] = []
    compact_entities: dict[str, dict] = {}

    for eid, edata in entities.items():
        etype = str(edata.get("type", "")).lower()
        if mentioned and etype not in mentioned:
            continue
        compact = {
            "id": eid,
            "type": etype,
            "name": edata.get("name", etype),
            "health": edata.get("health", 1.0),
        }
        compact_entities[eid] = compact
        nearby.append(compact)
        if etype in mentioned:
            target_entities.append(compact)

    # If nothing matched, include all entity types present
    if not compact_entities:
        for eid, edata in entities.items():
            etype = str(edata.get("type", "")).lower()
            compact = {"id": eid, "type": etype, "name": edata.get("name", etype)}
            compact_entities[eid] = compact
            nearby.append(compact)

    relevant_relations = [
        {
            "from": r.get("from_id", r.get("fromID", "")),
            "to": r.get("to_id", r.get("toID", "")),
            "type": r.get("type", ""),
            "strength": r.get("strength", 0.5),
        }
        for r in relationships[:20]
    ]

    return {
        "nearby_entities": nearby[:12],
        "target_entities": target_entities,
        "entities": compact_entities,
        "active_events": full_state.get("active_events", [])[:5],
        "relevant_relations": relevant_relations,
        "environmental_state": {
            "water_level": env.get("water_level", env.get("WaterLevel", 0)),
            "weather": env.get("weather", env.get("Weather", "clear")),
            "fire_spread": env.get("fire_spread", env.get("FireSpread", 0)),
        },
        "player_resources": full_state.get("player_resources", {}),
        "turn": turn,
    }
