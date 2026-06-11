from __future__ import annotations
from app.providers.knowledge import KnowledgeProvider, RetrievalQuery
from app.schemas import FramedDecision, ScenarioSpec
from app.providers.model import ModelProvider, ModelRequest
from app.core.config import get_settings


def build_scenarios(framed: FramedDecision, knowledge: KnowledgeProvider, model: ModelProvider | None = None) -> list[ScenarioSpec]:
    evidence = knowledge.retrieve(
        RetrievalQuery(
            case_id=framed.case_id,
            query=f"{framed.decision_type} scenario planning reversibility regret",
            decision_type=framed.decision_type,
            top_k=3,
        )
    )

    settings = get_settings()
    if settings.demo_mode or model is None or model.name == "mock":
        primary = framed.candidate_options[0].label
        experiment = framed.candidate_options[-1].label
        return [
            ScenarioSpec(
                scenario_key="optimistic",
                scenario_name="Controlled Upside Branch",
                narrative=(
                    f"The {primary} path works because the user converts urgency into disciplined validation. "
                    "Early momentum compounds into confidence, but the best outcome still depends on clear runway limits."
                ),
                branching_logic=[
                    "Core assumptions are tested in the first month.",
                    "Support system remains stable while the user absorbs ambiguity.",
                    "The user avoids irreversible commitments until evidence improves.",
                ],
                confidence_label="Credible upside, not guaranteed",
                probability_band="plausible but evidence-sensitive",
                time_horizon="6-18 months",
                upside_score=82,
                downside_score=38,
                regret_score=32,
                reversibility_score=62,
                optionality_score=74,
                evidence=evidence,
            ),
            ScenarioSpec(
                scenario_key="base",
                scenario_name="Evidence-Building Base Case",
                narrative=(
                    f"The {experiment} path produces the most useful information before a full commitment. "
                    "Progress is slower, but it preserves income, identity flexibility, and decision quality."
                ),
                branching_logic=[
                    "The first experiment reveals whether demand, fit, or motivation is real.",
                    "Savings remain intact long enough to choose from strength.",
                    "The user revisits the decision with better evidence rather than more rumination.",
                ],
                confidence_label="Most robust under uncertainty",
                probability_band="moderately likely",
                time_horizon="30-90 days before next checkpoint",
                upside_score=76,
                downside_score=24,
                regret_score=22,
                reversibility_score=88,
                optionality_score=91,
                evidence=evidence,
            ),
            ScenarioSpec(
                scenario_key="stress",
                scenario_name="Runway Compression Stress Case",
                narrative=(
                    "The downside branch appears when ambiguous signals are treated as proof. "
                    "Burn rate, isolation, delayed feedback, and status pressure narrow the user's future options."
                ),
                branching_logic=[
                    "The user commits before defining stop conditions.",
                    "Weak signals are overread because the decision already feels public.",
                    "Financial or emotional runway compresses before the next viable alternative is ready.",
                ],
                confidence_label="Stress test for fragile assumptions",
                probability_band="possible under poor guardrails",
                time_horizon="3-12 months",
                upside_score=44,
                downside_score=78,
                regret_score=68,
                reversibility_score=34,
                optionality_score=41,
                evidence=evidence,
            ),
        ]

    # Live Path using LLM
    system_prompt = (
        "You are the 'Scenario Lattice Agent'. Your job is to construct three diverse future scenario branches based on the user's framed decision:\n"
        "1. 'optimistic': An upside scenario where the user's main option succeeds because key assumptions hold and validation goes well.\n"
        "2. 'base': A realistic, information-building scenario that preserves optionality (typically a preparatory or experiment path).\n"
        "3. 'stress': A downside scenario representing structural stress, financial risk, or runway compression.\n"
        "\nFor each scenario, generate:\n"
        "- A scenario_name.\n"
        "- A narrative (1-2 sentences explaining what happens).\n"
        "- Branching logic (exactly 3 milestones/events that lead to this scenario).\n"
        "- A short confidence_label.\n"
        "- A probability_band description.\n"
        "- The time_horizon of this branch.\n"
        "- Scores between 0 and 100 for: upside_score, downside_score, regret_score, reversibility_score, optionality_score.\n"
        "\nYou MUST respond with a JSON object matching this structure:\n"
        "{\n"
        "  \"scenarios\": [\n"
        "    {\n"
        "      \"scenario_key\": \"optimistic\",\n"
        "      \"scenario_name\": \"...\",\n"
        "      \"narrative\": \"...\",\n"
        "      \"branching_logic\": [\"...\", \"...\", \"...\"],\n"
        "      \"confidence_label\": \"...\",\n"
        "      \"probability_band\": \"...\",\n"
        "      \"time_horizon\": \"...\",\n"
        "      \"upside_score\": 80,\n"
        "      \"downside_score\": 30,\n"
        "      \"regret_score\": 20,\n"
        "      \"reversibility_score\": 50,\n"
        "      \"optionality_score\": 60\n"
        "    },\n"
        "    {\n"
        "      \"scenario_key\": \"base\",\n"
        "      \"scenario_name\": \"...\",\n"
        "      \"narrative\": \"...\",\n"
        "      \"branching_logic\": [\"...\", \"...\", \"...\"],\n"
        "      \"confidence_label\": \"...\",\n"
        "      \"probability_band\": \"...\",\n"
        "      \"time_horizon\": \"...\",\n"
        "      \"upside_score\": 70,\n"
        "      \"downside_score\": 40,\n"
        "      \"regret_score\": 30,\n"
        "      \"reversibility_score\": 80,\n"
        "      \"optionality_score\": 85\n"
        "    },\n"
        "    {\n"
        "      \"scenario_key\": \"stress\",\n"
        "      \"scenario_name\": \"...\",\n"
        "      \"narrative\": \"...\",\n"
        "      \"branching_logic\": [\"...\", \"...\", \"...\"],\n"
        "      \"confidence_label\": \"...\",\n"
        "      \"probability_band\": \"...\",\n"
        "      \"time_horizon\": \"...\",\n"
        "      \"upside_score\": 30,\n"
        "      \"downside_score\": 80,\n"
        "      \"regret_score\": 70,\n"
        "      \"reversibility_score\": 30,\n"
        "      \"optionality_score\": 40\n"
        "    }\n"
        "  ]\n"
        "}"
    )

    payload = {
        "title": framed.title,
        "decision_type": framed.decision_type,
        "goals": framed.goals,
        "fears": framed.fears,
        "constraints": framed.constraints,
        "assumptions": framed.assumptions,
        "candidate_options": [opt.model_dump() for opt in framed.candidate_options],
        "evidence": [cit.model_dump() for cit in evidence],
    }

    result = model.complete_json(ModelRequest(system_prompt=system_prompt, user_payload=payload, schema_name="ScenarioLattice"))
    scenarios: list[ScenarioSpec] = []
    for item in result.get("scenarios", []):
        scenarios.append(
            ScenarioSpec(
                scenario_key=item.get("scenario_key", "base"),
                scenario_name=item.get("scenario_name", "Scenario"),
                narrative=item.get("narrative", ""),
                branching_logic=item.get("branching_logic", []),
                confidence_label=item.get("confidence_label", ""),
                probability_band=item.get("probability_band", ""),
                time_horizon=item.get("time_horizon", "12 months"),
                upside_score=item.get("upside_score", 50),
                downside_score=item.get("downside_score", 50),
                regret_score=item.get("regret_score", 50),
                reversibility_score=item.get("reversibility_score", 50),
                optionality_score=item.get("optionality_score", 50),
                evidence=evidence,
            )
        )
    return scenarios
