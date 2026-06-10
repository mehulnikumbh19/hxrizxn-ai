from __future__ import annotations

from app.schemas import FramedDecision, RegretAssessment, ScenarioSpec


def assess_regret(
    framed: FramedDecision,
    scenarios: list[ScenarioSpec],
    postcards: dict[str, str] | None = None,
) -> list[RegretAssessment]:
    output: list[RegretAssessment] = []
    for scenario in scenarios:
        key = scenario.scenario_key
        if key == "base":
            missed = 26
            action = 18
        elif key == "optimistic":
            missed = 18
            action = 38
        else:
            missed = 61
            action = 74

        postcard = (postcards or {}).get(key) or "Reflection from your future self."
        output.append(
            RegretAssessment(
                scenario_key=key,
                likely_regret_types=[
                    "missed-opportunity regret",
                    "action regret",
                    "identity drift regret",
                ],
                missed_opportunity_regret=missed,
                action_regret=action,
                identity_alignment_notes=(
                    f"The decision should protect the user's stated goals: {', '.join(framed.goals[:2])}."
                ),
                future_self_postcard=postcard,
            )
        )
    return output

