from __future__ import annotations
from app.schemas import FramedDecision, ScenarioSpec
from app.providers.model import ModelProvider, ModelRequest
from app.core.config import get_settings


def generate_future_self_postcards(framed: FramedDecision, scenarios: list[ScenarioSpec], model: ModelProvider | None = None) -> dict[str, str]:
    """Generate 'future self' reflections per scenario branch."""
    settings = get_settings()

    if settings.demo_mode or model is None or model.name == "mock":
        postcards = {}
        for scenario in scenarios:
            key = scenario.scenario_key
            if key == "base":
                postcard = (
                    "A year from now, future you is relieved that curiosity was honored without forcing a brittle leap."
                )
            elif key == "optimistic":
                postcard = (
                    "Future you is proud of the courage, but remembers that the courage worked because guardrails existed."
                )
            else:
                postcard = (
                    "Future you wishes the first move had been smaller, because the lesson was available before the full cost."
                )

            if framed.decision_type == "startup":
                if key == "base":
                    postcard = (
                        "A year from now, you are glad you ran a 30-day pilot before resigning. "
                        "The customer evidence you gathered saved you from quitting blindly."
                    )
            elif framed.decision_type == "relocation":
                if key == "base":
                    postcard = (
                        "A year from now, you appreciate that you tested the new country with a trial stay. "
                        "It helped you build a local network before committing to a one-way move."
                    )

            postcards[key] = postcard
        return postcards

    # Live Path using LLM
    system_prompt = (
        "You are the 'Future Self Agent'. Your job is to write creative, first-person 'postcards' sent from the user's future self back to their present self for each scenario branch.\n"
        "The postcard should reflect the emotional and practical state of the future self, reflecting on the choice they made.\n"
        "For each scenario key ('optimistic', 'base', 'stress'), write a reflective postcard of 2-3 sentences.\n"
        "\nYou MUST respond with a JSON object matching this structure:\n"
        "{\n"
        "  \"postcards\": {\n"
        "    \"optimistic\": \"...\",\n"
        "    \"base\": \"...\",\n"
        "    \"stress\": \"...\"\n"
        "  }\n"
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

    result = model.complete_json(ModelRequest(system_prompt=system_prompt, user_payload=payload, schema_name="FutureSelfPostcards"))
    return result.get("postcards", {})
