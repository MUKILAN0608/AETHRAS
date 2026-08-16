"""Strategic intent analysis — what the player is trying to achieve."""

import re

from app.prompt_schemas import StrategicIntent

_SPATIAL_BYPASS = re.compile(r"\b(without crossing|bypass|enters without|through walls|without walls)\b")
_MEMORY_ATTACK = re.compile(r"\b(ocean|mountain|city)\b.*\b(remember|remembers)\b")
_INDIRECT = re.compile(r"\b(don't destroy|do not destroy|without destroying|make .+ believe|foundation)\b")
_ENVIRONMENTAL = re.compile(r"\b(rise|flood|ocean|water|consume|consumes)\b")
_FIRE = re.compile(r"\b(fire|burn|ignite|catches fire)\b")
_CONTRADICTION = re.compile(r"\b(but remains|but still|yet remains)\b")


def analyze_strategy(normalized: str, entity_names: list[str]) -> StrategicIntent:
    """Infer strategic intent beyond literal wording."""
    if _CONTRADICTION.search(normalized):
        return StrategicIntent(
            strategy_type="CONFLICTING_TRANSFORMATION",
            target=entity_names[0].upper() if entity_names else "",
            objective="contradictory transformation",
            expected_effect="ambiguous outcome",
            confidence=0.55,
        )
    if _SPATIAL_BYPASS.search(normalized):
        return StrategicIntent(
            strategy_type="SPATIAL_BYPASS",
            target="fortress" if "fortress" in entity_names else (entity_names[-1] if entity_names else ""),
            objective="bypass physical defense",
            expected_effect="storm enters without wall breach",
            confidence=0.82,
        )
    if _INDIRECT.search(normalized):
        return StrategicIntent(
            strategy_type="INDIRECT_STRUCTURAL_ATTACK",
            target="fortress" if "fortress" in entity_names else "",
            objective="indirect structural damage",
            expected_effect="foundation weakened without direct destruction",
            confidence=0.86,
        )
    if _MEMORY_ATTACK.search(normalized):
        return StrategicIntent(
            strategy_type="MEMORY_ATTACK",
            target=entity_names[0].upper() if entity_names else "",
            objective="semantic memory manipulation",
            expected_effect="memory relation created or strengthened",
            confidence=0.78,
        )
    if _FIRE.search(normalized):
        return StrategicIntent(
            strategy_type="ENVIRONMENTAL_ATTACK",
            target=entity_names[-1].upper() if entity_names else "FOREST",
            objective="ignite and spread fire",
            expected_effect="vegetation destroyed",
            confidence=0.88,
        )
    if _ENVIRONMENTAL.search(normalized):
        return StrategicIntent(
            strategy_type="ENVIRONMENTAL_ATTACK",
            target=entity_names[-1].upper() if entity_names else "FORTRESS",
            objective="flood or submerge target",
            expected_effect="water level rise",
            confidence=0.87,
        )
    return StrategicIntent(
        strategy_type="UNKNOWN",
        objective="unclear",
        expected_effect="unknown",
        confidence=0.4,
    )
