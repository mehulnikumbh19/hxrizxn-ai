from __future__ import annotations

from app.schemas import (
    AgentTraceView,
    DecisionIntake,
    DecisionMemo,
    ExperimentPlan,
    FramedDecision,
    OptionalityAssessment,
    RegretAssessment,
    RiskItem,
    SafetyFlag,
    ScenarioImpact,
    ScenarioSpec,
)


def test_required_json_schema_exports_are_valid():
    models = [
        DecisionIntake,
        FramedDecision,
        ScenarioSpec,
        ScenarioImpact,
        RiskItem,
        RegretAssessment,
        OptionalityAssessment,
        ExperimentPlan,
        DecisionMemo,
        SafetyFlag,
        AgentTraceView,
    ]
    for model in models:
        schema = model.model_json_schema()
        assert schema["title"] == model.__name__
        assert "properties" in schema

