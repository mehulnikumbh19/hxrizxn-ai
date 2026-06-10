from __future__ import annotations

from app.agents.safety import default_disclaimer
from app.schemas import (
    DecisionMemo,
    ExperimentPlan,
    FramedDecision,
    OptionalityAssessment,
    RegretAssessment,
    RiskItem,
    ScenarioSpec,
)


def compose_memo(
    framed: FramedDecision,
    scenarios: list[ScenarioSpec],
    risks: list[RiskItem],
    optionality: list[OptionalityAssessment],
    regret: list[RegretAssessment],
    experiment: ExperimentPlan,
) -> DecisionMemo:
    base = next(scenario for scenario in scenarios if scenario.scenario_key == "base")
    top_risks = ", ".join(risk.risk_name for risk in risks[:3])
    best_optionality = max(optionality, key=lambda item: item.optionality_score)
    regret_note = min(regret, key=lambda item: item.action_regret)
    return DecisionMemo(
        recommendation_summary=(
            "Proceed via experiment: do not make the full irreversible move yet. "
            f"Use {experiment.plan_name} as the next commitment."
        ),
        rationale=(
            f"HORIZON-X favors the {base.scenario_name} because it preserves optionality "
            f"({best_optionality.optionality_score}/100), reduces action regret, and converts the decision "
            "from a single leap into evidence-generating milestones."
        ),
        uncertainty_notes=(
            "The largest unknowns are not personality flaws; they are evidence gaps. "
            f"Watch these risks first: {top_risks}."
        ),
        safer_next_move=experiment.steps[0],
        disclaimers=default_disclaimer(framed.high_stakes_flags),
        citations=framed.evidence + base.evidence,
    )

