"""Prompt normalization stage."""

import re


def normalize(prompt: str) -> tuple[str, str]:
    """
    Normalize prompt text while preserving original.

    Returns (original_prompt, normalized_prompt).
    """
    original = prompt.strip()
    normalized = original
    normalized = re.sub(r"!+", ".", normalized)
    normalized = re.sub(r"\.{2,}", ".", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = normalized.strip(" .")
    if normalized and normalized[-1] not in ".!?":
        normalized += "."
    # Lowercase non-proper handling for matching (keep display original)
    normalized = normalized.lower()
    return original, normalized
