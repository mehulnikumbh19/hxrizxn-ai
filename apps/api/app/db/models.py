from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def _uuid() -> str:
    return str(uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    email: Mapped[str | None] = mapped_column(String(320), unique=True, nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)
    settings_json: Mapped[dict] = mapped_column(JSON, default=dict)


class DecisionCase(Base):
    __tablename__ = "decision_cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(240))
    decision_type: Mapped[str] = mapped_column(String(80), default="life")
    raw_prompt: Mapped[str] = mapped_column(Text)
    structured_context_json: Mapped[dict] = mapped_column(JSON, default=dict)
    time_horizon_months: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    options: Mapped[list["DecisionOptionDB"]] = relationship(cascade="all, delete-orphan")
    scenarios: Mapped[list["ScenarioDB"]] = relationship(cascade="all, delete-orphan")
    agent_runs: Mapped[list["AgentRunDB"]] = relationship(cascade="all, delete-orphan")


class DecisionOptionDB(Base):
    __tablename__ = "decision_options"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    case_id: Mapped[str] = mapped_column(ForeignKey("decision_cases.id", ondelete="CASCADE"))
    option_key: Mapped[str] = mapped_column(String(60))
    label: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ScenarioDB(Base):
    __tablename__ = "scenarios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    case_id: Mapped[str] = mapped_column(ForeignKey("decision_cases.id", ondelete="CASCADE"))
    option_id: Mapped[str | None] = mapped_column(ForeignKey("decision_options.id"), nullable=True)
    scenario_key: Mapped[str] = mapped_column(String(60))
    scenario_name: Mapped[str] = mapped_column(String(180))
    narrative: Mapped[str] = mapped_column(Text)
    confidence_label: Mapped[str] = mapped_column(String(80))
    probability_band: Mapped[str] = mapped_column(String(80))
    time_horizon: Mapped[str] = mapped_column(String(120))
    upside_score: Mapped[int] = mapped_column(Integer)
    downside_score: Mapped[int] = mapped_column(Integer)
    regret_score: Mapped[int] = mapped_column(Integer)
    reversibility_score: Mapped[int] = mapped_column(Integer)
    optionality_score: Mapped[int] = mapped_column(Integer)
    evidence_json: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    impacts: Mapped[list["ScenarioImpactDB"]] = relationship(cascade="all, delete-orphan")
    risks: Mapped[list["ScenarioRiskDB"]] = relationship(cascade="all, delete-orphan")


class ScenarioImpactDB(Base):
    __tablename__ = "scenario_impacts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    scenario_id: Mapped[str] = mapped_column(ForeignKey("scenarios.id", ondelete="CASCADE"))
    domain: Mapped[str] = mapped_column(String(80))
    order_level: Mapped[int] = mapped_column(Integer)
    impact_direction: Mapped[str] = mapped_column(String(40))
    severity: Mapped[int] = mapped_column(Integer)
    explanation: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ScenarioRiskDB(Base):
    __tablename__ = "scenario_risks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    scenario_id: Mapped[str] = mapped_column(ForeignKey("scenarios.id", ondelete="CASCADE"))
    risk_name: Mapped[str] = mapped_column(String(160))
    risk_type: Mapped[str] = mapped_column(String(80))
    likelihood_band: Mapped[str] = mapped_column(String(80))
    severity_band: Mapped[str] = mapped_column(String(80))
    detectability_band: Mapped[str] = mapped_column(String(80))
    mitigation: Mapped[str] = mapped_column(Text)
    black_swan: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class ExperimentPlanDB(Base):
    __tablename__ = "experiment_plans"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    case_id: Mapped[str] = mapped_column(ForeignKey("decision_cases.id", ondelete="CASCADE"))
    plan_name: Mapped[str] = mapped_column(String(180))
    hypothesis: Mapped[str] = mapped_column(Text)
    duration_days: Mapped[int] = mapped_column(Integer)
    reversible: Mapped[bool] = mapped_column(Boolean)
    steps_json: Mapped[list] = mapped_column(JSON, default=list)
    success_criteria_json: Mapped[list] = mapped_column(JSON, default=list)
    stop_conditions_json: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class AgentRunDB(Base):
    __tablename__ = "agent_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    case_id: Mapped[str] = mapped_column(ForeignKey("decision_cases.id", ondelete="CASCADE"))
    agent_name: Mapped[str] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(40))
    input_json: Mapped[dict] = mapped_column(JSON, default=dict)
    output_json: Mapped[dict] = mapped_column(JSON, default=dict)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    token_usage_json: Mapped[dict] = mapped_column(JSON, default=dict)
    error_text: Mapped[str | None] = mapped_column(Text, nullable=True)


class DocumentDB(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    case_id: Mapped[str] = mapped_column(ForeignKey("decision_cases.id", ondelete="CASCADE"))
    filename: Mapped[str] = mapped_column(String(260))
    mime_type: Mapped[str] = mapped_column(String(120))
    storage_uri: Mapped[str] = mapped_column(String(600))
    text_status: Mapped[str] = mapped_column(String(40), default="pending")
    retrieval_status: Mapped[str] = mapped_column(String(40), default="mock-indexed")
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class FinalRecommendationDB(Base):
    __tablename__ = "final_recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    case_id: Mapped[str] = mapped_column(ForeignKey("decision_cases.id", ondelete="CASCADE"))
    recommendation_summary: Mapped[str] = mapped_column(Text)
    rationale: Mapped[str] = mapped_column(Text)
    uncertainty_notes: Mapped[str] = mapped_column(Text)
    disclaimers: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

