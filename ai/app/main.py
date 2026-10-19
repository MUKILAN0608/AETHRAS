"""
AETHRAS AI Service — FastAPI application.

Phase 3: Prompt Intelligence Engine with legacy /api/parse compatibility.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.decision_engine.decision_router import evaluate_decision
from app.research_logger import log_decision
from app.health import router as health_router
from app.parser import parse_prompt
from app.prompt_engine.pipeline import pipeline
from app.prompt_schemas import (
    CompileRequest,
    InterpretRequest,
    InterpretResponse,
    ValidateRequest,
    ValidationResult,
    ValidationStatus,
)
from app.schemas import ParsedActionResponse, PromptRequest

app = FastAPI(
    title="AETHRAS AI Service",
    description="AI/ML inference service for AETHRAS — Prompt Intelligence Engine",
    version="0.3.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)


@app.post("/api/parse", response_model=ParsedActionResponse)
async def parse_prompt_endpoint(request: PromptRequest) -> ParsedActionResponse:
    """Legacy mock parser (Phase 2 compatibility)."""
    return parse_prompt(request)


@app.post("/api/v1/prompt/interpret", response_model=InterpretResponse)
async def interpret_prompt(request: InterpretRequest) -> InterpretResponse:
    """Run full Prompt Intelligence Engine pipeline."""
    response = pipeline.interpret(request)
    # Whitelist compact facts: never forward arbitrary client context/history.
    entities = request.world_context.get("entities", {})
    referenced = {entity.entity_id for entity in response.interpretation.entities if entity.entity_id}
    facts = {str(k): {field: value.get(field) for field in ("type", "health")}
             for k, value in entities.items() if k in referenced and isinstance(value, dict)} if isinstance(entities, dict) else {}
    environment = request.world_context.get("environmental_state", {})
    if not isinstance(environment, dict):
        environment = {}
    state = {
        "prompt": request.prompt,
        "intent": response.interpretation.intent.value,
        "entities": [{"name": e.name, "id": e.entity_id, "resolution": e.resolution}
                     for e in response.interpretation.entities],
        "relationships": [r.model_dump(mode="json") for r in response.interpretation.relationships],
        "constraints": [c.model_dump(mode="json") for c in response.interpretation.constraints],
        "world": {"entities": facts, "turn": request.turn,
                  "environment": {k: environment.get(k)
                                  for k in ("water_level", "weather", "fire_spread")}},
        "validation": response.validation.model_dump(mode="json"),
        "critic": response.critic_findings,
    }
    candidates = [response.action] if response.action and response.status == "VALID" else []
    response.decision = await evaluate_decision(state, candidates, settings)
    if response.decision.review_required and response.status == "VALID":
        response.status = response.validation.status = ValidationStatus.AMBIGUOUS
        response.validation.reasons.append("Decision policy requires review; reinterpret before execution")
    response.latency.total_ms += response.decision.latency_ms
    log_decision(request, response)
    return response


@app.post("/api/v1/prompt/compile")
async def compile_prompt(request: CompileRequest):
    """Compile interpretation into action without full pipeline."""
    action, validation = pipeline.compile_only(request)
    return {"action": action, "validation": validation}


@app.post("/api/v1/prompt/validate", response_model=ValidationResult)
async def validate_prompt_action(request: ValidateRequest) -> ValidationResult:
    """Validate a compiled action proposal."""
    return pipeline.validate_only(request)


@app.get("/api/v1/prompt/health")
async def prompt_engine_health():
    """Prompt Intelligence Engine health."""
    return {
        "service": "prompt-intelligence-engine",
        "status": "ok",
        "provider": settings.llm_provider,
        "version": "0.3.0",
        "decision_engine": {"enabled": settings.aethras_decision_enabled,
                            "provider": settings.aethras_decision_provider,
                            "model": settings.decision_model, "configured": settings.decision_configured,
                            "fallback_policy": "require_review"},
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
        log_level=settings.log_level,
    )
