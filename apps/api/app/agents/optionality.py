from __future__ import annotations
from app.schemas import FramedDecision, OptionalityAssessment, ScenarioSpec
from app.providers.model import ModelProvider, ModelRequest
from app.core.config import get_settings


def score_optionality(framed: FramedDecision, scenarios: list[ScenarioSpec], model: ModelProvider | None = None) -> list[OptionalityAssessment]:
    settings = get_settings()

    if settings.demo_mode or model is None or model.name == "mock":
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

    # Live Path using LLM
    system_prompt = (
        "You are the 'Reversibility and Optionality Agent'. Your job is to analyze the lock-in and option preservation details of the user's decision paths for each scenario.\n"
        "Given the framed decision brief and scenario branches, evaluate the structural lock-in (how hard it is to undo this choice) and recommend option preservation moves.\n"
        "For each scenario key ('optimistic', 'base', 'stress'), generate:\n"
        "- scenario_key ('optimistic', 'base', 'stress')\n"
        "- reversibility_score (0 to 100, where 100 is fully reversible, 0 is a one-way door)\n"
        "- optionality_score (0 to 100, where 100 opens new paths, 0 closes all other options)\n"
        "- lock_in_explanation (a sentence explaining what forces lock-in or costs for this branch)\n"
        "- option_preservation_moves (list of exactly 3 specific actions to keep fallback paths warm or reduce lock-in)\n"
        "\nYou MUST respond with a JSON object matching this structure:\n"
        "{\n"
        "  \"assessments\": [\n"
        "    {\n"
        "      \"scenario_key\": \"optimistic\",\n"
        "      \"reversibility_score\": 60,\n"
        "      \"optionality_score\": 75,\n"
        "      \"lock_in_explanation\": \"...\",\n"
        "      \"option_preservation_moves\": [\"...\", \"...\", \"...\"]\n"
        "    },\n"
        "    ...\n"
        "  ]\n"
        "}"
    )

    payload = {
        "title": framed.title,
        "decision_type": framed.decision_type,
        "goals": framed.goals,
        "fears": framed.fears,
        "constraints": framed.constraints,
        "candidate_options": [opt.model_dump() for opt in framed.candidate_options],
        "scenarios": [sc.model_dump(exclude={"evidence"}) for sc in scenarios],
    }

    result = model.complete_json(ModelRequest(system_prompt=system_prompt, user_payload=payload, schema_name="OptionalityScore"))
    assessments: list[OptionalityAssessment] = []
    for item in result.get("assessments", []):
        assessments.append(
            OptionalityAssessment(
                scenario_key=item.get("scenario_key", "base"),
                reversibility_score=item.get("reversibility_score", 50),
                optionality_score=item.get("optionality_score", 50),
                lock_in_explanation=item.get("lock_in_explanation", ""),
                option_preservation_moves=item.get("option_preservation_moves", []),
            )
        )
    return assessments
