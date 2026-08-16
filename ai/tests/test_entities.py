"""Tests for entity extraction."""

from app.prompt_engine.entity_extractor import extract_entity_names, resolve_entities


def test_extract_ocean_fortress():
    names = extract_entity_names("the ocean rises and consumes the fortress.")
    assert "ocean" in names
    assert "fortress" in names


def test_resolve_found_entity():
    ctx = {
        "entities": {
            "fortress_01": {"type": "fortress", "name": "Fortress"},
        }
    }
    refs = resolve_entities(["fortress"], ctx)
    assert refs[0].resolved is True
    assert refs[0].entity_id == "fortress_01"


def test_resolve_moon_not_found():
    refs = resolve_entities(["moon"], {})
    assert refs[0].resolution == "NOT_FOUND"
