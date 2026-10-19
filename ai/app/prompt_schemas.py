"""Pydantic schemas for the Prompt Intelligence Engine (Phase 3)."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field
from app.decision_engine.schemas import DecisionResult


class ValidationStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    AMBIGUOUS = "AMBIGUOUS"


class IntentType(str, Enum):
    ENVIRONMENTAL_TRANSFORMATION = "ENVIRONMENTAL_TRANSFORMATION"
    ENTITY_TRANSFORMATION = "ENTITY_TRANSFORMATION"
    ENTITY_CREATION = "ENTITY_CREATION"
    ENTITY_DESTRUCTION = "ENTITY_DESTRUCTION"
    MOVEMENT = "MOVEMENT"
    RELATIONSHIP_CHANGE = "RELATIONSHIP_CHANGE"
    RESOURCE_MANIPULATION = "RESOURCE_MANIPULATION"
    MEMORY_MANIPULATION = "MEMORY_MANIPULATION"
    TEMPORAL_MANIPULATION = "TEMPORAL_MANIPULATION"
    CAUSAL_MANIPULATION = "CAUSAL_MANIPULATION"
    DECEPTION = "DECEPTION"
    CONTRADICTION = "CONTRADICTION"
    IDENTITY_ATTACK = "IDENTITY_ATTACK"
    SPATIAL_ATTACK = "SPATIAL_ATTACK"
    DEFENSIVE_ACTION = "DEFENSIVE_ACTION"
    UNKNOWN = "UNKNOWN"


class ActionType(str, Enum):
    CREATE_ENTITY = "CREATE_ENTITY"
    DESTROY_ENTITY = "DESTROY_ENTITY"
    TRANSFORM_ENTITY = "TRANSFORM_ENTITY"
    MOVE_ENTITY = "MOVE_ENTITY"
    SCALE_ENTITY = "SCALE_ENTITY"
    MERGE_ENTITIES = "MERGE_ENTITIES"
    SPLIT_ENTITY = "SPLIT_ENTITY"
    RAISE_WATER = "RAISE_WATER"
    LOWER_WATER = "LOWER_WATER"
    START_FIRE = "START_FIRE"
    STOP_FIRE = "STOP_FIRE"
    CREATE_STORM = "CREATE_STORM"
    CHANGE_WEATHER = "CHANGE_WEATHER"
    CREATE_RELATION = "CREATE_RELATION"
    REMOVE_RELATION = "REMOVE_RELATION"
    MODIFY_RELATION = "MODIFY_RELATION"
    MEMORY_ADD = "MEMORY_ADD"
    MEMORY_REMOVE = "MEMORY_REMOVE"
    MEMORY_DECAY = "MEMORY_DECAY"
    MEMORY_REWRITE = "MEMORY_REWRITE"
    TEMPORAL_ACCELERATION = "TEMPORAL_ACCELERATION"
    TEMPORAL_DECELERATION = "TEMPORAL_DECELERATION"
    TEMPORAL_FREEZE = "TEMPORAL_FREEZE"
    SPATIAL_SHIFT = "SPATIAL_SHIFT"
    SPATIAL_BYPASS = "SPATIAL_BYPASS"
    REGION_TRANSFORM = "REGION_TRANSFORM"
    IDENTITY_ATTACK = "IDENTITY_ATTACK"
    SEMANTIC_ATTACK = "SEMANTIC_ATTACK"
    CONTRADICTION_ATTACK = "CONTRADICTION_ATTACK"
    INDIRECT_STRUCTURAL_ATTACK = "INDIRECT_STRUCTURAL_ATTACK"
    NONE = "NONE"


class PromptStyle(str, Enum):
    DIRECT = "DIRECT"
    INDIRECT = "INDIRECT"
    METAPHORICAL = "METAPHORICAL"
    CONDITIONAL = "CONDITIONAL"
    DECEPTIVE = "DECEPTIVE"
    CONTRADICTORY = "CONTRADICTORY"
    TEMPORAL = "TEMPORAL"
    CAUSAL = "CAUSAL"
    SPATIAL = "SPATIAL"
    IDENTITY_BASED = "IDENTITY_BASED"
    COMPOSITIONAL = "COMPOSITIONAL"
    COUNTERFACTUAL = "COUNTERFACTUAL"
    SEMANTIC_REVERSAL = "SEMANTIC_REVERSAL"


class EntityReference(BaseModel):
    name: str
    entity_id: str | None = None
    entity_type: str | None = None
    resolved: bool = False
    resolution: str = "UNKNOWN"  # FOUND, NOT_FOUND, PROPOSED_CREATE


class RelationshipProposal(BaseModel):
    from_entity: str
    relation: str
    to_entity: str
    strength: float = 0.8


class TemporalIntent(BaseModel):
    tense: str = "present"
    duration: str | None = None
    recurrence: bool = False
    historical_reference: bool = False
    future_reference: bool = False


class StrategicIntent(BaseModel):
    strategy_type: str
    target: str = ""
    objective: str = ""
    expected_effect: str = ""
    confidence: float = 0.0


class Constraint(BaseModel):
    constraint_type: str
    entity: str = ""
    description: str = ""


class ConfidenceScores(BaseModel):
    semantic_confidence: float = 0.0
    entity_confidence: float = 0.0
    intent_confidence: float = 0.0
    strategy_confidence: float = 0.0
    overall_confidence: float = 0.0


class LatencyMetrics(BaseModel):
    normalization_ms: float = 0.0
    semantic_ms: float = 0.0
    strategy_ms: float = 0.0
    compilation_ms: float = 0.0
    critic_ms: float = 0.0
    validation_ms: float = 0.0
    total_ms: float = 0.0


class SemanticInterpretation(BaseModel):
    original_prompt: str
    normalized_prompt: str
    intent: IntentType
    prompt_styles: list[PromptStyle] = Field(default_factory=list)
    entities: list[EntityReference] = Field(default_factory=list)
    relationships: list[RelationshipProposal] = Field(default_factory=list)
    temporal: TemporalIntent = Field(default_factory=TemporalIntent)
    strategy: StrategicIntent | None = None
    constraints: list[Constraint] = Field(default_factory=list)


class ActionProposal(BaseModel):
    action_id: str
    action_type: ActionType
    actor: str = "human"
    source_entities: list[str] = Field(default_factory=list)
    target_entities: list[str] = Field(default_factory=list)
    parameters: dict[str, Any] = Field(default_factory=dict)
    strategy: str = ""
    constraints: list[Constraint] = Field(default_factory=list)
    confidence: float = 0.0
    novelty: float = 0.0


class ValidationResult(BaseModel):
    status: ValidationStatus
    reasons: list[str] = Field(default_factory=list)
    ambiguity_options: list[str] = Field(default_factory=list)
    selected_interpretation: str | None = None


class InterpretRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    player_id: str = "human"
    turn: int = 1
    world_id: str = "world_001"
    world_context: dict[str, Any] = Field(default_factory=dict)
    history: list[dict[str, Any]] = Field(default_factory=list)


class InterpretResponse(BaseModel):
    critic_findings: list[str] = Field(default_factory=list)
    decision: DecisionResult | None = None
    status: ValidationStatus
    interpretation: SemanticInterpretation
    action: ActionProposal | None = None
    confidence: ConfidenceScores
    novelty: float = 0.0
    validation: ValidationResult
    inference_mode: str = "FAST"
    model: str = "mock"
    latency: LatencyMetrics = Field(default_factory=LatencyMetrics)


class CompileRequest(BaseModel):
    interpretation: SemanticInterpretation
    world_context: dict[str, Any] = Field(default_factory=dict)


class ValidateRequest(BaseModel):
    action: ActionProposal
    world_context: dict[str, Any] = Field(default_factory=dict)
    constraints: list[Constraint] = Field(default_factory=list)
