from __future__ import annotations
from app.schemas import FramedDecision, ScenarioImpact, ScenarioSpec
from app.providers.model import ModelProvider, ModelRequest
from app.core.config import get_settings


DOMAINS = [
    "finances",
    "career",
    "health_energy",
    "relationships",
    "location_lifestyle",
    "learning_identity",
]


def map_ripple_effects(framed: FramedDecision, scenarios: list[ScenarioSpec], model: ModelProvider | None = None) -> list[ScenarioImpact]:
    settings = get_settings()

    if settings.demo_mode or model is None or model.name == "mock":
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

    # Live Path using LLM
    system_prompt = (
        "You are the 'Ripple Effects Agent'. Your job is to map and evaluate the first, second, and third-order consequences of the user's decision paths across different life/business domains.\n"
        "Given the framed decision brief and a list of scenario branches, project impacts across these domains:\n"
        "- 'finances'\n"
        "- 'career'\n"
        "- 'health_energy'\n"
        "- 'relationships'\n"
        "- 'location_lifestyle'\n"
        "- 'learning_identity'\n"
        "\nFor each scenario, generate a series of ripple impacts. For each impact, specify:\n"
        "- scenario_key (must match one of the scenarios: 'optimistic', 'base', 'stress')\n"
        "- domain (must be one of: 'finances', 'career', 'health_energy', 'relationships', 'location_lifestyle', 'learning_identity')\n"
        "- order_level (must be 1, 2, or 3 representing first-order, second-order, or third-order consequence)\n"
        "- impact_direction (must be 'positive', 'negative', 'mixed', or 'neutral')\n"
        "- severity (1 to 5, where 1 is minimal and 5 is extreme impact)\n"
        "- explanation (a detailed sentence detailing how this ripple effect manifests)\n"
        "\nGenerate at least 3 distinct impact items for each of the three scenarios (optimistic, base, stress).\n"
        "\nYou MUST respond with a JSON object matching this structure:\n"
        "{\n"
        "  \"impacts\": [\n"
        "    {\n"
        "      \"scenario_key\": \"optimistic\",\n"
        "      \"domain\": \"finances\",\n"
        "      \"order_level\": 1,\n"
        "      \"impact_direction\": \"positive\",\n"
        "      \"severity\": 3,\n"
        "      \"explanation\": \"...\"\n"
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

    result = model.complete_json(ModelRequest(system_prompt=system_prompt, user_payload=payload, schema_name="RippleEffects"))
    impacts: list[ScenarioImpact] = []
    for item in result.get("impacts", []):
        impacts.append(
            ScenarioImpact(
                scenario_key=item.get("scenario_key", "base"),
                domain=item.get("domain", "career"),
                order_level=item.get("order_level", 1),
                impact_direction=item.get("impact_direction", "neutral"),
                severity=item.get("severity", 3),
                explanation=item.get("explanation", ""),
            )
        )
    return impacts
