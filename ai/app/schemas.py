"""Pydantic schemas for AI service requests and responses."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    service: str = "aethras-ai"
    status: str = "ok"


class PromptRequest(BaseModel):
    prompt: str = Field(..., min_length=1)


class ParsedActionResponse(BaseModel):
    """
    Structured action parsed from natural language.
    DEMO / PLACEHOLDER — mock semantic parser, not a real LLM.
    """

    intent: str
    action: str
    target: str
    source: str = ""
    intensity: float = Field(default=0.8, ge=0.0, le=1.0)
    magnitude: float = Field(default=0.7, ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    demo: bool = Field(default=True)
