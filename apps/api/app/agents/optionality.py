from __future__ import annotations

from app.schemas import FramedDecision, OptionalityAssessment, ScenarioSpec


def score_optionality(framed: FramedDecision, scenarios: list[ScenarioSpec]) -> list[OptionalityAssessment]:
    assessments: list[OptionalityAssessment] = []
    for scenario in scenarios:
        assessments.append(
            OptionalityAssessment(
                scenario_key=scenario.scenario_key,
                reversibility_score=scenario.reversibility_score,
                optionality_score=scenario.optionality_score,
                lock_in_explanation=(
                    "Lock-in rises when cash runway, public identity, legal commitments, or location constraints "
                    "make reversal expensive."
                ),
                option_preservation_moves=[
                    "Set a predefined review date and stop condition.",
                    "Keep a credible fallback path warm before announcing irreversible changes.",
                    "Convert the decision into a smaller proof-of-traction milestone.",
                ],
            )
        )
    return assessments

