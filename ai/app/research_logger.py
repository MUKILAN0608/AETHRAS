"""Research experiment logging for prompt intelligence."""

import json
from datetime import datetime, timezone
from pathlib import Path

from app.prompt_schemas import (
    ActionProposal,
    ConfidenceScores,
    LatencyMetrics,
    SemanticInterpretation,
    ValidationResult,
)

_LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
_LOG_FILE = _LOG_DIR / "experiments.jsonl"


def log_experiment(
    *,
    match_id: str,
    turn: int,
    player_id: str,
    original_prompt: str,
    normalized_prompt: str,
    interpretation: SemanticInterpretation,
    action: ActionProposal | None,
    confidence: ConfidenceScores,
    novelty: float,
    validation: ValidationResult,
    latency: LatencyMetrics,
    model: str,
    inference_mode: str,
) -> None:
    """Append one experiment record per prompt."""
    _LOG_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "match_id": match_id,
        "turn": turn,
        "player_id": player_id,
        "original_prompt": original_prompt,
        "normalized_prompt": normalized_prompt,
        "intent": interpretation.intent.value,
        "entities": [e.model_dump() for e in interpretation.entities],
        "relationships": [r.model_dump() for r in interpretation.relationships],
        "strategy": interpretation.strategy.model_dump() if interpretation.strategy else None,
        "constraints": [c.model_dump() for c in interpretation.constraints],
        "action": action.model_dump() if action else None,
        "confidence": confidence.model_dump(),
        "novelty": novelty,
        "validation_result": validation.model_dump(),
        "latency_ms": latency.model_dump(),
        "model": model,
        "inference_mode": inference_mode,
    }
    with _LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
