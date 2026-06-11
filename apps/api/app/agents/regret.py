from __future__ import annotations
from app.schemas import FramedDecision, RegretAssessment, ScenarioSpec
from app.providers.model import ModelProvider, ModelRequest
from app.core.config import get_settings


def assess_regret(
    framed: FramedDecision,
    scenarios: list[ScenarioSpec],
    postcards: dict[str, str] | None = None,
    model: ModelProvider | None = None,
) -> list[RegretAssessment]:
    settings = get_settings()

    if settings.demo_mode or model is None or model.name == "mock":
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

    # Live Path using LLM
    system_prompt = (
        "You are the 'Regret Assessment Agent'. Your job is to evaluate regret dynamics for each scenario branch.\n"
        "Analyze the user's framed decision brief and scenario details to estimate regret metrics.\n"
        "For each scenario key ('optimistic', 'base', 'stress'), generate:\n"
        "- scenario_key ('optimistic', 'base', 'stress')\n"
        "- likely_regret_types (list of regret types, e.g. ['missed-opportunity regret', 'action regret', 'identity drift'])\n"
        "- missed_opportunity_regret (score 0 to 100)\n"
        "- action_regret (score 0 to 100)\n"
        "- identity_alignment_notes (sentence explaining how this branch aligns or conflicts with the user's core goals)\n"
        "\nYou MUST respond with a JSON object matching this structure:\n"
        "{\n"
        "  \"assessments\": [\n"
        "    {\n"
        "      \"scenario_key\": \"optimistic\",\n"
        "      \"likely_regret_types\": [\"...\", \"...\"],\n"
        "      \"missed_opportunity_regret\": 20,\n"
        "      \"action_regret\": 40,\n"
        "      \"identity_alignment_notes\": \"...\"\n"
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

    result = model.complete_json(ModelRequest(system_prompt=system_prompt, user_payload=payload, schema_name="RegretAssessment"))
    output: list[RegretAssessment] = []
    for item in result.get("assessments", []):
        key = item.get("scenario_key", "base")
        postcard = (postcards or {}).get(key) or "Reflection from your future self."
        output.append(
            RegretAssessment(
                scenario_key=key,
                likely_regret_types=item.get("likely_regret_types", []),
                missed_opportunity_regret=item.get("missed_opportunity_regret", 50),
                action_regret=item.get("action_regret", 50),
                identity_alignment_notes=item.get("identity_alignment_notes", ""),
                future_self_postcard=postcard,
            )
        )
    return output
