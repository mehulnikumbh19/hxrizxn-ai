"""initial hxrizxn schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-10
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=True, unique=True),
        sa.Column("display_name", sa.String(length=160), nullable=True),
        sa.Column("settings_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        *_timestamps(),
    )
    op.create_table(
        "decision_cases",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("title", sa.String(length=240), nullable=False),
        sa.Column("decision_type", sa.String(length=80), nullable=False),
        sa.Column("raw_prompt", sa.Text(), nullable=False),
        sa.Column("structured_context_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("time_horizon_months", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="draft"),
        *_timestamps(),
    )
    op.create_table(
        "decision_options",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("case_id", sa.String(length=36), sa.ForeignKey("decision_cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("option_key", sa.String(length=60), nullable=False),
        sa.Column("label", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "scenarios",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("case_id", sa.String(length=36), sa.ForeignKey("decision_cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("option_id", sa.String(length=36), sa.ForeignKey("decision_options.id"), nullable=True),
        sa.Column("scenario_key", sa.String(length=60), nullable=False),
        sa.Column("scenario_name", sa.String(length=180), nullable=False),
        sa.Column("narrative", sa.Text(), nullable=False),
        sa.Column("confidence_label", sa.String(length=80), nullable=False),
        sa.Column("probability_band", sa.String(length=80), nullable=False),
        sa.Column("time_horizon", sa.String(length=120), nullable=False),
        sa.Column("upside_score", sa.Integer(), nullable=False),
        sa.Column("downside_score", sa.Integer(), nullable=False),
        sa.Column("regret_score", sa.Integer(), nullable=False),
        sa.Column("reversibility_score", sa.Integer(), nullable=False),
        sa.Column("optionality_score", sa.Integer(), nullable=False),
        sa.Column("evidence_json", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "scenario_impacts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("scenario_id", sa.String(length=36), sa.ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("domain", sa.String(length=80), nullable=False),
        sa.Column("order_level", sa.Integer(), nullable=False),
        sa.Column("impact_direction", sa.String(length=40), nullable=False),
        sa.Column("severity", sa.Integer(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "scenario_risks",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("scenario_id", sa.String(length=36), sa.ForeignKey("scenarios.id", ondelete="CASCADE"), nullable=False),
        sa.Column("risk_name", sa.String(length=160), nullable=False),
        sa.Column("risk_type", sa.String(length=80), nullable=False),
        sa.Column("likelihood_band", sa.String(length=80), nullable=False),
        sa.Column("severity_band", sa.String(length=80), nullable=False),
        sa.Column("detectability_band", sa.String(length=80), nullable=False),
        sa.Column("mitigation", sa.Text(), nullable=False),
        sa.Column("black_swan", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "experiment_plans",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("case_id", sa.String(length=36), sa.ForeignKey("decision_cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("plan_name", sa.String(length=180), nullable=False),
        sa.Column("hypothesis", sa.Text(), nullable=False),
        sa.Column("duration_days", sa.Integer(), nullable=False),
        sa.Column("reversible", sa.Boolean(), nullable=False),
        sa.Column("steps_json", sa.JSON(), nullable=False),
        sa.Column("success_criteria_json", sa.JSON(), nullable=False),
        sa.Column("stop_conditions_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "agent_runs",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("case_id", sa.String(length=36), sa.ForeignKey("decision_cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("agent_name", sa.String(length=120), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("input_json", sa.JSON(), nullable=False),
        sa.Column("output_json", sa.JSON(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("token_usage_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("error_text", sa.Text(), nullable=True),
    )
    op.create_table(
        "documents",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("case_id", sa.String(length=36), sa.ForeignKey("decision_cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filename", sa.String(length=260), nullable=False),
        sa.Column("mime_type", sa.String(length=120), nullable=False),
        sa.Column("storage_uri", sa.String(length=600), nullable=False),
        sa.Column("text_status", sa.String(length=40), nullable=False),
        sa.Column("retrieval_status", sa.String(length=40), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_table(
        "final_recommendations",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("case_id", sa.String(length=36), sa.ForeignKey("decision_cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("recommendation_summary", sa.Text(), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("uncertainty_notes", sa.Text(), nullable=False),
        sa.Column("disclaimers", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    for table in [
        "final_recommendations",
        "documents",
        "agent_runs",
        "experiment_plans",
        "scenario_risks",
        "scenario_impacts",
        "scenarios",
        "decision_options",
        "decision_cases",
        "users",
    ]:
        op.drop_table(table)

