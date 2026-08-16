"""Prompt Intelligence Engine — multi-stage pipeline."""

import time

from app.llm.router import get_provider
from app.prompt_engine.action_compiler import compile_action
from app.prompt_engine.action_validator import validate_action
from app.prompt_engine.ambiguity import detect_ambiguity
from app.prompt_engine.confidence import compute_confidence
from app.prompt_engine.constraint_extractor import extract_constraints
from app.prompt_engine.critic import critique
from app.prompt_engine.entity_extractor import extract_entity_names, resolve_entities
from app.prompt_engine.intent_detector import detect_intent
from app.prompt_engine.novelty import compute_novelty
from app.prompt_engine.normalizer import normalize
from app.prompt_engine.relation_extractor import extract_relationships
from app.prompt_engine.strategic_analyzer import analyze_strategy
from app.prompt_engine.style_classifier import classify_styles
from app.prompt_engine.temporal_analyzer import analyze_temporal
from app.prompt_schemas import (
    CompileRequest,
    InterpretRequest,
    InterpretResponse,
    SemanticInterpretation,
    ValidateRequest,
    ValidationStatus,
)
from app.research_logger import log_experiment


def _elapsed_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 2)


class PromptPipeline:
    """Full interpret → compile → critic → validate pipeline."""

    def __init__(self) -> None:
        self._provider = get_provider("fast")

    def interpret(self, request: InterpretRequest) -> InterpretResponse:
        total_start = time.perf_counter()
        latencies: dict[str, float] = {}

        # Stage: Normalize
        t0 = time.perf_counter()
        original, normalized = normalize(request.prompt)
        latencies["normalization_ms"] = _elapsed_ms(t0)

        # Stage: Semantic parsing
        t0 = time.perf_counter()
        entity_names = extract_entity_names(normalized)
        intent = detect_intent(normalized)
        entities = resolve_entities(entity_names, request.world_context)
        relationships = extract_relationships(normalized, entity_names)
        temporal = analyze_temporal(normalized)
        styles = classify_styles(normalized)
        latencies["semantic_ms"] = _elapsed_ms(t0)

        # Stage: Strategic analysis
        t0 = time.perf_counter()
        strategy = analyze_strategy(normalized, entity_names)
        constraints = extract_constraints(normalized, entity_names)
        latencies["strategy_ms"] = _elapsed_ms(t0)

        interpretation = SemanticInterpretation(
            original_prompt=original,
            normalized_prompt=normalized,
            intent=intent,
            prompt_styles=styles,
            entities=entities,
            relationships=relationships,
            temporal=temporal,
            strategy=strategy,
            constraints=constraints,
        )

        # Stage: Compile
        t0 = time.perf_counter()
        action = compile_action(interpretation)
        latencies["compilation_ms"] = _elapsed_ms(t0)

        # Stage: Critic
        t0 = time.perf_counter()
        critic_warnings = critique(interpretation, action)
        latencies["critic_ms"] = _elapsed_ms(t0)

        # Stage: Validate + ambiguity
        t0 = time.perf_counter()
        amb_status, amb_reasons, amb_options = detect_ambiguity(interpretation, action)
        validation = validate_action(
            action, request.world_context, constraints
        ) if action else None

        if validation and validation.status == ValidationStatus.VALID and amb_status != ValidationStatus.VALID:
            validation.status = amb_status
            validation.reasons = amb_reasons
            validation.ambiguity_options = amb_options
        elif validation is None:
            from app.prompt_schemas import ValidationResult
            validation = ValidationResult(
                status=amb_status,
                reasons=amb_reasons or ["No action compiled"],
                ambiguity_options=amb_options,
            )

        # Critic can downgrade VALID → INVALID for unsupported entities
        if any("unsupported_entity" in w or "hallucinated_entity" in w for w in critic_warnings):
            from app.prompt_schemas import ValidationResult
            validation = ValidationResult(
                status=ValidationStatus.INVALID,
                reasons=[w for w in critic_warnings if "entity" in w],
            )

        latencies["validation_ms"] = _elapsed_ms(t0)
        latencies["total_ms"] = _elapsed_ms(total_start)

        confidence = compute_confidence(interpretation, action)
        novelty = compute_novelty(action, request.history)
        if action:
            action.novelty = novelty
            action.confidence = confidence.overall_confidence

        inference_mode = "DEEP" if confidence.overall_confidence < 0.6 else "FAST"
        model_name = self._provider.provider_id

        from app.prompt_schemas import LatencyMetrics

        response = InterpretResponse(
            status=validation.status,
            interpretation=interpretation,
            action=action,
            confidence=confidence,
            novelty=novelty,
            validation=validation,
            inference_mode=inference_mode,
            model=model_name,
            latency=LatencyMetrics(**latencies),
        )

        log_experiment(
            match_id=request.world_id,
            turn=request.turn,
            player_id=request.player_id,
            original_prompt=original,
            normalized_prompt=normalized,
            interpretation=interpretation,
            action=action,
            confidence=confidence,
            novelty=novelty,
            validation=validation,
            latency= response.latency,
            model=model_name,
            inference_mode=inference_mode,
        )

        return response

    def compile_only(self, request: CompileRequest):
        action = compile_action(request.interpretation)
        validation = validate_action(
            action, request.world_context, request.interpretation.constraints
        ) if action else None
        return action, validation

    def validate_only(self, request: ValidateRequest):
        return validate_action(
            request.action, request.world_context, request.constraints
        )


pipeline = PromptPipeline()
