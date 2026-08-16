"""Tests for prompt normalizer."""

from app.prompt_engine.normalizer import normalize


def test_normalize_preserves_original():
    original, normalized = normalize("The ocean rises!")
    assert original == "The ocean rises!"
    assert "ocean" in normalized


def test_normalize_lowercases():
    _, normalized = normalize("FORTRESS")
    assert normalized == "fortress."

def test_normalize_collapses_whitespace():
    _, normalized = normalize("ocean   rises")
    assert "  " not in normalized
