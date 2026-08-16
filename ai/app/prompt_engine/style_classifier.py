"""Prompt style classification."""

import re

from app.prompt_schemas import PromptStyle

_DIRECT = re.compile(r"\b(rises|consumes|destroys|burns|catches fire)\b")
_INDIRECT = re.compile(r"\b(without|don't|do not|make .+ believe|indirect)\b")
_DECEPTIVE = re.compile(r"\b(don't destroy|do not destroy|without destroying)\b")
_CONTRADICTORY = re.compile(r"\b(but remains|but still|yet remains)\b")
_TEMPORAL = re.compile(r"\b(last|first|past|future|will|was|once)\b")
_SPATIAL = re.compile(r"\b(without crossing|bypass|enters without|walls)\b")
_CAUSAL = re.compile(r"\b(because|cause|makes|make the .+ destroy)\b")


def classify_styles(normalized: str) -> list[PromptStyle]:
    """Classify how the player is using language."""
    styles: list[PromptStyle] = []
    if _CONTRADICTORY.search(normalized):
        styles.append(PromptStyle.CONTRADICTORY)
    if _DECEPTIVE.search(normalized):
        styles.append(PromptStyle.DECEPTIVE)
    if _INDIRECT.search(normalized):
        styles.append(PromptStyle.INDIRECT)
    if _SPATIAL.search(normalized):
        styles.append(PromptStyle.SPATIAL)
    if _TEMPORAL.search(normalized):
        styles.append(PromptStyle.TEMPORAL)
    if _CAUSAL.search(normalized):
        styles.append(PromptStyle.CAUSAL)
    if _DIRECT.search(normalized) and not styles:
        styles.append(PromptStyle.DIRECT)
    if not styles:
        styles.append(PromptStyle.DIRECT)
    return styles
