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
from app.providers.model import ModelProvider, ModelRequest
from app.core.config import get_settings


def compose_memo(
    framed: FramedDecision,
    scenarios: list[ScenarioSpec],
    risks: list[RiskItem],
    optionality: list[OptionalityAssessment],
    regret: list[RegretAssessment],
    experiment: ExperimentPlan,
    model: ModelProvider | None = None,
) -> DecisionMemo:
    settings = get_settings()

    if settings.demo_mode or model is None or model.name == "mock":
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

    # Live Path using LLM
    system_prompt = (
        "You are the 'Recommendation Composer Agent'. Your job is to draft a comprehensive final Decision Memo that synthesizes the entire analysis.\n"
        "Analyze the user's framed decision, the simulated scenarios, the identified risks, the optionality/regret assessments, and the experiment plan.\n"
        "Write a clear, objective, high-agency recommendation.\n"
        "Extract:\n"
        "- recommendation_summary (a 1-2 sentence recommendation on how the user should proceed, typically starting with the validation experiment)\n"
        "- rationale (a detailed explanation of the logic, highlighting optionality and regret dynamics)\n"
        "- uncertainty_notes (specific discussion of the largest unknowns and evidence gaps)\n"
        "- safer_next_move (the very first concrete step the user should take immediately to start validating or preparing)\n"
        "\nYou MUST respond with a JSON object matching this structure:\n"
        "{\n"
        "  \"recommendation_summary\": \"...\",\n"
        "  \"rationale\": \"...\",\n"
        "  \"uncertainty_notes\": \"...\",\n"
        "  \"safer_next_move\": \"...\"\n"
        "}"
    )

    base_scenario = next((s for s in scenarios if s.scenario_key == "base"), scenarios[0])
    payload = {
        "title": framed.title,
        "decision_type": framed.decision_type,
        "goals": framed.goals,
        "fears": framed.fears,
        "constraints": framed.constraints,
        "candidate_options": [opt.model_dump() for opt in framed.candidate_options],
        "scenarios": [sc.model_dump(exclude={"evidence"}) for sc in scenarios],
        "risks": [risk.model_dump() for risk in risks],
        "optionality": [opt.model_dump() for opt in optionality],
        "regret": [reg.model_dump() for reg in regret],
        "experiment": experiment.model_dump(),
    }

    result = model.complete_json(ModelRequest(system_prompt=system_prompt, user_payload=payload, schema_name="DecisionMemo"))
    return DecisionMemo(
        recommendation_summary=result.get("recommendation_summary", ""),
        rationale=result.get("rationale", ""),
        uncertainty_notes=result.get("uncertainty_notes", ""),
        safer_next_move=result.get("safer_next_move", ""),
        disclaimers=default_disclaimer(framed.high_stakes_flags),
        citations=framed.evidence + base_scenario.evidence,
    )
