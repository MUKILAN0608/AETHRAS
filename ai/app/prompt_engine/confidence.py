"""Confidence scoring for prompt interpretations."""

from app.prompt_schemas import (
    ActionProposal,
    ConfidenceScores,
    EntityReference,
    IntentType,
    SemanticInterpretation,
    StrategicIntent,
)


def compute_confidence(
    interpretation: SemanticInterpretation,
    action: ActionProposal | None,
) -> ConfidenceScores:
    """Compute layered confidence scores without exposing chain-of-thought."""
    entities = interpretation.entities
    resolved = sum(1 for e in entities if e.resolved)
    entity_conf = resolved / len(entities) if entities else 0.5

    intent_conf = 0.87 if interpretation.intent != IntentType.UNKNOWN else 0.35

    strategy = interpretation.strategy
    strategy_conf = strategy.confidence if strategy else 0.4

    semantic_conf = 0.91
    if interpretation.intent == IntentType.CONTRADICTION:
        semantic_conf = 0.55
    elif interpretation.intent == IntentType.UNKNOWN:
        semantic_conf = 0.4

    overall = (
        semantic_conf * 0.3
        + entity_conf * 0.25
        + intent_conf * 0.25
        + strategy_conf * 0.2
    )
    if action:
        overall = (overall + action.confidence) / 2

    return ConfidenceScores(
        semantic_confidence=round(semantic_conf, 2),
        entity_confidence=round(entity_conf, 2),
        intent_confidence=round(intent_conf, 2),
        strategy_confidence=round(strategy_conf, 2),
        overall_confidence=round(min(overall, 0.99), 2),
    )
