"""Temporal interpretation stage."""

import re

from app.prompt_schemas import TemporalIntent

_PAST = re.compile(r"\b(was|were|once|used to|historically|last battle|first battle|past)\b")
_FUTURE = re.compile(r"\b(will|shall|tomorrow|future|going to)\b")
_CONTINUOUS = re.compile(r"\b(keep|keeps|continues|spreading|ongoing)\b")
_HISTORICAL = re.compile(r"\b(remembers the|remember the|last attack|first battle|history)\b")


def analyze_temporal(normalized: str) -> TemporalIntent:
    """Detect temporal concepts in prompt."""
    tense = "present"
    if _PAST.search(normalized):
        tense = "past"
    elif _FUTURE.search(normalized):
        tense = "future"

    return TemporalIntent(
        tense=tense,
        duration="continuous" if _CONTINUOUS.search(normalized) else None,
        recurrence=bool(_CONTINUOUS.search(normalized)),
        historical_reference=bool(_HISTORICAL.search(normalized)),
        future_reference=bool(_FUTURE.search(normalized)),
    )
