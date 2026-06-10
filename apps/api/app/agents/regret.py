from __future__ import annotations

from app.schemas import FramedDecision, RegretAssessment, ScenarioSpec


def assess_regret(framed: FramedDecision, scenarios: list[ScenarioSpec]) -> list[RegretAssessment]:
    output: list[RegretAssessment] = []
    for scenario in scenarios:
        if scenario.scenario_key == "base":
            missed = 26
            action = 18
            postcard = (
                "A year from now, future you is relieved that curiosity was honored without forcing a brittle leap."
            )
        elif scenario.scenario_key == "optimistic":
            missed = 18
            action = 38
            postcard = (
                "Future you is proud of the courage, but remembers that the courage worked because guardrails existed."
            )
        else:
            missed = 61
            action = 74
            postcard = (
                "Future you wishes the first move had been smaller, because the lesson was available before the full cost."
            )
        output.append(
            RegretAssessment(
                scenario_key=scenario.scenario_key,
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

