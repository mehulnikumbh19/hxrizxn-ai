from __future__ import annotations

from app.schemas import (
    ExperimentPlan,
    FramedDecision,
    RiskItem,
    SafetyFlag,
    ScenarioImpact,
    ScenarioSpec,
)


class VerificationResult(dict):
    @property
    def approved(self) -> bool:
        return bool(self["approved"])


def verify_outputs(
    framed: FramedDecision,
    scenarios: list[ScenarioSpec],
    impacts: list[ScenarioImpact],
    risks: list[RiskItem],
    experiment: ExperimentPlan,
) -> VerificationResult:
    flags: list[SafetyFlag] = list(framed.high_stakes_flags)
    scenario_keys = {scenario.scenario_key for scenario in scenarios}
    impact_keys = {impact.scenario_key for impact in impacts}
    risk_keys = {risk.scenario_key for risk in risks if risk.scenario_key in scenario_keys}
    notes: list[str] = []
    if scenario_keys != {"optimistic", "base", "stress"}:
        notes.append("Scenario lattice must include optimistic, base, and stress branches.")
    if not scenario_keys.issubset(impact_keys):
        notes.append("Every scenario requires ripple effects.")
    if not scenario_keys.issubset(risk_keys):
        notes.append("Every scenario requires risk coverage.")
    if not experiment.reversible:
        notes.append("Experiment plan should be reversible for MVP safety posture.")
    for flag in flags:
        if flag.severity == "block":
            notes.append(f"Blocked unsafe domain: {flag.domain}.")
    return VerificationResult(
        approved=not any(flag.severity == "block" for flag in flags) and not notes,
        safety_flags=[flag.model_dump() for flag in flags],
        confidence_notes=notes or ["Structured outputs are internally consistent and experiment-first."],
        revision_target=None if not notes else "upstream-agent",
    )

