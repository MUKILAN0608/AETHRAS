"""
AETHRAS AI Service — FastAPI application.

Phase 3: Prompt Intelligence Engine with legacy /api/parse compatibility.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.health import router as health_router
from app.parser import parse_prompt
from app.prompt_engine.pipeline import pipeline
from app.prompt_schemas import (
    CompileRequest,
    InterpretRequest,
    InterpretResponse,
    ValidateRequest,
    ValidationResult,
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
    return pipeline.interpret(request)


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
