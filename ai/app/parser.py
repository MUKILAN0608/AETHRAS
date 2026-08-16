"""
Mock semantic parser — DEMO / PLACEHOLDER (Phase 2).

Deterministic keyword matching for controlled semantic events.
NOT a real LLM.
"""

import re

from app.schemas import ParsedActionResponse, PromptRequest

_FLOOD = re.compile(r"\b(ocean|water|flood|sea|tide|rain|submerge|drown|rise|lake|river)\b", re.I)
_FIRE = re.compile(r"\b(fire|burn|burns|burning|ignite|flame|catch fire|catches fire|caught fire)\b", re.I)
_FOREST = re.compile(r"\b(forest|woods|grove|trees|woodland)\b", re.I)
_FORTRESS = re.compile(r"\b(fortress|castle|tower|keep|stronghold|citadel)\b", re.I)
_OCEAN = re.compile(r"\b(ocean|sea|water|tide)\b", re.I)
_MOUNTAIN = re.compile(r"\b(mountain|peak|summit|hill)\b", re.I)
_CITY = re.compile(r"\b(city|town|civilization|kingdom)\b", re.I)
_MEMORY_DECAY = re.compile(r"\b(forget|forgets|memory|past|decay|fading)\b", re.I)
_LIE = re.compile(r"\b(lie|lies|liar|deceive|dishonest|false)\b", re.I)
_REMEMBER = re.compile(r"\b(remember|remembers|recall|memory)\b", re.I)
_STORM = re.compile(r"\b(storm|storms|lightning|thunder|tempest)\b", re.I)
_CREATE = re.compile(r"\b(appear|appears|create|spawn|bridge)\b", re.I)


def parse_prompt(request: PromptRequest) -> ParsedActionResponse:
    text = request.prompt.strip()

    # Test Prompt 3: "The mountain remembers this lie."
    if _MOUNTAIN.search(text) and (_LIE.search(text) or _REMEMBER.search(text)):
        return ParsedActionResponse(
            intent="semantic_event",
            action="MEMORY_REMEMBER",
            target="MOUNTAIN",
            source="",
            intensity=0.8,
            magnitude=0.85,
            confidence=0.92,
            demo=True,
        )

    # Memory decay: "The city forgets its past."
    if _MEMORY_DECAY.search(text) and _CITY.search(text):
        return ParsedActionResponse(
            intent="semantic_event",
            action="MEMORY_DECAY",
            target="CITY",
            intensity=0.7,
            magnitude=0.7,
            confidence=0.88,
            demo=True,
        )

    # Test Prompt 2: "The forest catches fire."
    if _FIRE.search(text) and _FOREST.search(text):
        return ParsedActionResponse(
            intent="environmental_action",
            action="FIRE",
            target="FOREST",
            source="",
            intensity=0.85,
            magnitude=0.85,
            confidence=0.91,
            demo=True,
        )

    if _FIRE.search(text):
        target = "FOREST" if _FOREST.search(text) else "UNKNOWN"
        return ParsedActionResponse(
            intent="environmental_action",
            action="FIRE",
            target=target,
            intensity=0.75,
            confidence=0.80,
            demo=True,
        )

    # Test Prompt 1: "The ocean rises."
    if _FLOOD.search(text):
        target = "FORTRESS" if _FORTRESS.search(text) else "OCEAN"
        if _CITY.search(text):
            target = "CITY"
        source = "OCEAN" if _OCEAN.search(text) else ""
        return ParsedActionResponse(
            intent="environmental_action",
            action="FLOOD",
            target=target,
            source=source,
            intensity=0.8 if not _FORTRESS.search(text) else 0.9,
            magnitude=0.8,
            confidence=0.90 if _FORTRESS.search(text) else 0.85,
            demo=True,
        )

    if _STORM.search(text):
        return ParsedActionResponse(
            intent="environmental_action",
            action="STORM",
            target="WORLD",
            intensity=0.7,
            confidence=0.82,
            demo=True,
        )

    if _CREATE.search(text):
        target = "BRIDGE" if "bridge" in text.lower() else "ENTITY"
        return ParsedActionResponse(
            intent="creation_action",
            action="CREATE",
            target=target,
            intensity=0.6,
            confidence=0.75,
            demo=True,
        )

    return ParsedActionResponse(
        intent="unknown_action",
        action="NONE",
        target="NONE",
        confidence=0.10,
        demo=True,
    )
