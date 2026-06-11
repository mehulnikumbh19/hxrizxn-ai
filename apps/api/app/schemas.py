from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

Band = Literal["low", "medium", "high", "very_high"]
ScenarioKey = Literal["optimistic", "base", "stress"]


class Citation(BaseModel):
    title: str
    source: str
    snippet: str
    confidence: Band = "medium"


class DecisionOption(BaseModel):
    option_key: str
    label: str
    description: str


class DecisionIntake(BaseModel):
    title: str | None = None
    decision_type: str = "life"
    raw_prompt: str = Field(min_length=12)
    goals: list[str] = Field(default_factory=list)
    fears: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    money_limit_months: int | None = Field(default=None, ge=0, le=240)
    time_horizon_months: int | None = Field(default=12, ge=1, le=240)
    dependencies: list[str] = Field(default_factory=list)
    uploaded_document_ids: list[str] = Field(default_factory=list)


class SafetyFlag(BaseModel):
    domain: str
    severity: Literal["info", "caution", "escalate", "block"]
    message: str
    recommended_boundary: str


class FramedDecision(BaseModel):
    case_id: str | None = None
    title: str
    decision_type: str
    goals: list[str]
    fears: list[str]
    constraints: list[str]
    assumptions: list[str]
    missing_information: list[str]
    candidate_options: list[DecisionOption]
    high_stakes_flags: list[SafetyFlag] = Field(default_factory=list)
    evidence: list[Citation] = Field(default_factory=list)


class ScenarioImpact(BaseModel):
    scenario_key: str
    domain: Literal["finances", "career", "health_energy", "relationships", "location_lifestyle", "learning_identity"]
    order_level: Literal[1, 2, 3]
    impact_direction: Literal["positive", "negative", "mixed", "neutral"]
    severity: int = Field(ge=1, le=5)
    explanation: str

    @field_validator("domain", mode="before")
    @classmethod
    def normalize_domain(cls, value: Any) -> Any:
        aliases = {
            "finance": "finances",
            "financial": "finances",
            "money": "finances",
            "relationship": "relationships",
            "social": "relationships",
            "health": "health_energy",
            "energy": "health_energy",
            "location": "location_lifestyle",
            "lifestyle": "location_lifestyle",
            "learning": "learning_identity",
            "identity": "learning_identity",
        }
        if isinstance(value, str):
            key = value.strip().lower().replace("-", "_").replace(" ", "_")
            return aliases.get(key, key)
        return value

    @field_validator("impact_direction", mode="before")
    @classmethod
    def normalize_impact_direction(cls, value: Any) -> Any:
        aliases = {
            "upside": "positive",
            "benefit": "positive",
            "downside": "negative",
            "risk": "negative",
            "balanced": "mixed",
            "uncertain": "mixed",
        }
        if isinstance(value, str):
            key = value.strip().lower().replace("-", "_").replace(" ", "_")
            return aliases.get(key, key)
        return value


class RiskItem(BaseModel):
    scenario_key: str
    risk_name: str
    risk_type: Literal["common", "hidden", "black_swan", "safety", "execution"]
    likelihood_band: Band
    severity_band: Band
    detectability_band: Band
    mitigation: str
    black_swan: bool = False

    @field_validator("risk_type", mode="before")
    @classmethod
    def normalize_risk_type(cls, value: Any) -> Any:
        aliases = {
            "black swan": "black_swan",
            "blackswan": "black_swan",
            "operational": "execution",
            "implementation": "execution",
            "unknown": "hidden",
        }
        if isinstance(value, str):
            key = value.strip().lower().replace("-", "_")
            return aliases.get(key, key)
        return value

    @field_validator("likelihood_band", "severity_band", "detectability_band", mode="before")
    @classmethod
    def normalize_band(cls, value: Any) -> Any:
        aliases = {
            "very high": "very_high",
            "very-high": "very_high",
            "critical": "very_high",
            "moderate": "medium",
        }
        if isinstance(value, str):
            key = value.strip().lower()
            return aliases.get(key, key.replace("-", "_").replace(" ", "_"))
        return value


class ScenarioSpec(BaseModel):
    scenario_key: ScenarioKey
    scenario_name: str
    narrative: str
    branching_logic: list[str]
    confidence_label: str
    probability_band: str
    time_horizon: str
    upside_score: int = Field(ge=0, le=100)
    downside_score: int = Field(ge=0, le=100)
    regret_score: int = Field(ge=0, le=100)
    reversibility_score: int = Field(ge=0, le=100)
    optionality_score: int = Field(ge=0, le=100)
    evidence: list[Citation] = Field(default_factory=list)


class RegretAssessment(BaseModel):
    scenario_key: str
    likely_regret_types: list[str]
    missed_opportunity_regret: int = Field(ge=0, le=100)
    action_regret: int = Field(ge=0, le=100)
    identity_alignment_notes: str
    future_self_postcard: str


class OptionalityAssessment(BaseModel):
    scenario_key: str
    reversibility_score: int = Field(ge=0, le=100)
    optionality_score: int = Field(ge=0, le=100)
    lock_in_explanation: str
    option_preservation_moves: list[str]


class ExperimentPlan(BaseModel):
    plan_name: str
    hypothesis: str
    duration_days: int = Field(ge=1, le=180)
    reversible: bool
    steps: list[str]
    success_criteria: list[str]
    stop_conditions: list[str]
    what_you_will_learn: list[str]


class DecisionMemo(BaseModel):
    recommendation_summary: str
    rationale: str
    uncertainty_notes: str
    safer_next_move: str
    disclaimers: str
    citations: list[Citation] = Field(default_factory=list)


class AgentTraceView(BaseModel):
    agent_name: str
    status: str
    input_summary: str
    output_summary: str
    started_at: datetime
    completed_at: datetime | None = None
    latency_ms: int


class AnalysisPackage(BaseModel):
    case_id: str
    horizon_x_stage: str = "X - Explain recommendation, uncertainty, and evidence"
    framed_decision: FramedDecision
    scenarios: list[ScenarioSpec]
    impacts: list[ScenarioImpact]
    risks: list[RiskItem]
    optionality: list[OptionalityAssessment]
    regret: list[RegretAssessment]
    experiment_plan: ExperimentPlan
    safety_flags: list[SafetyFlag]
    memo: DecisionMemo
    trace: list[AgentTraceView]


class CaseCreateRequest(DecisionIntake):
    pass


class CaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    decision_type: str
    raw_prompt: str
    structured_context_json: dict[str, Any]
    time_horizon_months: int | None
    status: str
    created_at: datetime
    updated_at: datetime


class DocumentResponse(BaseModel):
    id: str
    filename: str
    mime_type: str
    storage_uri: str
    text_status: str
    retrieval_status: str
