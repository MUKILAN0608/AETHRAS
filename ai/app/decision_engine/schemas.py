from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

Probability = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False, strict=True)]


class ChoiceAnswer(BaseModel):
    type: Literal["choice"]
    choice: str
    probabilities: dict[str, Probability]
    confidence: Probability


class ScoreAnswer(BaseModel):
    type: Literal["score"]
    score: float = Field(ge=0, le=2, allow_inf_nan=False, strict=True)
    legend: dict[str, str]
    probabilities: dict[str, Probability]
    confidence: Probability


class NoulAnswer(BaseModel):
    type: Literal["noul"]
    noul: Probability
    confidence: Probability | None = None


Answer = Annotated[ChoiceAnswer | ScoreAnswer | NoulAnswer, Field(discriminator="type")]


class Usage(BaseModel):
    input_tokens: int = Field(ge=0, strict=True)
    output_tokens: int = Field(ge=0, strict=True)


class ProviderResponse(BaseModel):
    model: str = Field(min_length=1)
    answers: dict[str, Answer]
    usage: Usage


class DecisionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version: str = "decision-v3"
    provider: str = "unknown"
    provider_request_id: str | None = None
    billed_credits: int | None = None
    billing_status: str = "not_reported"
    request_id: str
    status: str = "disabled"
    invoked: bool = False
    model: str | None = None
    resolved_model: str | None = None
    candidate_ids: list[str] = Field(default_factory=list)
    selected_candidate: str | None = None
    confidence: float | None = None
    strategic_impact: float | None = None
    review_required: bool = False
    simulation_recommended: bool = False
    review_probability: float | None = None
    simulation_probability: float | None = None
    latency_ms: float = 0
    attempts: int = 0
    fallback: bool = False
    reason: str | None = None
    usage: dict[str, int] = Field(default_factory=dict)
    probabilities: dict[str, dict[str, float]] = Field(default_factory=dict)
