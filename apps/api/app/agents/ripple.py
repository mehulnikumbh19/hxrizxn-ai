from __future__ import annotations

from app.schemas import FramedDecision, ScenarioImpact, ScenarioSpec


DOMAINS = [
    "finances",
    "career",
    "health_energy",
    "relationships",
    "location_lifestyle",
    "learning_identity",
]


def map_ripple_effects(framed: FramedDecision, scenarios: list[ScenarioSpec]) -> list[ScenarioImpact]:
    impacts: list[ScenarioImpact] = []
    for scenario in scenarios:
        for index, domain in enumerate(DOMAINS):
            base_severity = 2 + ((index + len(scenario.scenario_key)) % 3)
            direction = "positive" if scenario.scenario_key == "optimistic" else "mixed"
            if scenario.scenario_key == "stress" and domain in {"finances", "health_energy", "relationships"}:
                direction = "negative"
                base_severity = 5
            impacts.append(
                ScenarioImpact(
                    scenario_key=scenario.scenario_key,
                    domain=domain,  # type: ignore[arg-type]
                    order_level=1,
                    impact_direction=direction,  # type: ignore[arg-type]
                    severity=base_severity,
                    explanation=f"Immediate {domain.replace('_', '/')} impact from choosing under {framed.decision_type} uncertainty.",
                )
            )
            impacts.append(
                ScenarioImpact(
                    scenario_key=scenario.scenario_key,
                    domain=domain,  # type: ignore[arg-type]
                    order_level=2,
                    impact_direction="mixed",
                    severity=min(5, base_severity + 1),
                    explanation=(
                        f"Second-order {domain.replace('_', '/')} effect emerges as the first decision changes "
                        "time, money, identity, or social support."
                    ),
                )
            )
            if domain in {"career", "learning_identity", "finances"}:
                impacts.append(
                    ScenarioImpact(
                        scenario_key=scenario.scenario_key,
                        domain=domain,  # type: ignore[arg-type]
                        order_level=3,
                        impact_direction="mixed",
                        severity=min(5, base_severity + 1),
                        explanation=(
                            "Third-order consequence: the decision changes the next set of opportunities "
                            "the user is eligible, energized, or liquid enough to pursue."
                        ),
                    )
                )
    return impacts

