"""Relationship extraction stage."""

import re

from app.prompt_schemas import RelationshipProposal

_RELATION_VERBS = {
    "consumes": "CONSUMES",
    "consume": "CONSUMES",
    "protects": "PROTECTS",
    "protect": "PROTECTS",
    "attacks": "ATTACKS",
    "attack": "ATTACKS",
    "destroys": "DESTROYS",
    "destroy": "DESTROYS",
    "remembers": "REMEMBERS",
    "remember": "REMEMBERS",
    "enters": "ENTERS",
    "surrounds": "SURROUNDS",
    "threatens": "THREATENS",
}


def extract_relationships(normalized: str, entity_names: list[str]) -> list[RelationshipProposal]:
    """Extract relationship proposals from prompt."""
    relations: list[RelationshipProposal] = []
    if len(entity_names) < 2:
        return relations

    verb = "AFFECTS"
    for v, rel_type in _RELATION_VERBS.items():
        if re.search(rf"\b{v}\b", normalized):
            verb = rel_type
            break

    relations.append(
        RelationshipProposal(
            from_entity=entity_names[0].upper(),
            relation=verb,
            to_entity=entity_names[1].upper(),
            strength=0.85,
        )
    )
    return relations
