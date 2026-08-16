"""Intent detection stage."""

import re

from app.prompt_schemas import IntentType

_FLOOD = re.compile(r"\b(ocean|water|flood|sea|tide|rain|submerge|drown|rise|river|lake)\b")
_FIRE = re.compile(r"\b(fire|burn|burns|burning|ignite|flame|catch fire|catches fire)\b")
_MEMORY = re.compile(r"\b(remember|remembers|recall|memory|forget|forgets|past)\b")
_STORM = re.compile(r"\b(storm|storms|lightning|thunder|tempest)\b")
_CREATE = re.compile(r"\b(appear|appears|create|spawn|bridge)\b")
_DESTROY = re.compile(r"\b(destroy|destroys|demolish|crush|consume|consumes)\b")
_SPATIAL = re.compile(r"\b(without crossing|bypass|enters without|through walls|without walls)\b")
_CONTRADICTION = re.compile(r"\b(but remains|but still|yet remains|never existed)\b")
_DECEPTION = re.compile(r"\b(don't destroy|do not destroy|without destroying|make .+ believe)\b")
_TRANSFORM = re.compile(r"\b(becomes|become|transform|turns into|turn into)\b")
_PROTECT = re.compile(r"\b(protect|protects|refuses to let|defend|defends)\b")


def detect_intent(normalized: str) -> IntentType:
    """Classify high-level player intent from normalized prompt."""
    if _CONTRADICTION.search(normalized):
        return IntentType.CONTRADICTION
    if _DECEPTION.search(normalized):
        return IntentType.DECEPTION
    if _SPATIAL.search(normalized):
        return IntentType.SPATIAL_ATTACK
    if _MEMORY.search(normalized):
        return IntentType.MEMORY_MANIPULATION
    if _FLOOD.search(normalized) and _DESTROY.search(normalized):
        return IntentType.ENVIRONMENTAL_TRANSFORMATION
    if _FLOOD.search(normalized):
        return IntentType.ENVIRONMENTAL_TRANSFORMATION
    if _FIRE.search(normalized):
        return IntentType.ENVIRONMENTAL_TRANSFORMATION
    if _STORM.search(normalized):
        return IntentType.ENVIRONMENTAL_TRANSFORMATION
    if _CREATE.search(normalized):
        return IntentType.ENTITY_CREATION
    if _DESTROY.search(normalized):
        return IntentType.ENTITY_DESTRUCTION
    if _TRANSFORM.search(normalized):
        return IntentType.ENTITY_TRANSFORMATION
    if _PROTECT.search(normalized):
        return IntentType.DEFENSIVE_ACTION
    return IntentType.UNKNOWN
