from __future__ import annotations
from app.schemas import FramedDecision, RiskItem, ScenarioSpec
from app.providers.model import ModelProvider, ModelRequest
from app.core.config import get_settings


def identify_risks(framed: FramedDecision, scenarios: list[ScenarioSpec], model: ModelProvider | None = None) -> list[RiskItem]:
    settings = get_settings()

    if settings.demo_mode or model is None or model.name == "mock":
        risks: list[RiskItem] = []
        for scenario in scenarios:
            key = scenario.scenario_key
            risks.extend(
                [
                    RiskItem(
                        scenario_key=key,
                        risk_name="Runway compression",
                        risk_type="execution",
                        likelihood_band="medium" if key != "stress" else "high",
                        severity_band="high",
                        detectability_band="medium",
                        mitigation="Define a cash floor, weekly burn review, and automatic stop condition before commitment.",
                        black_swan=False,
                    ),
                    RiskItem(
                        scenario_key=key,
                        risk_name="Narrative lock-in",
                        risk_type="hidden",
                        likelihood_band="medium",
                        severity_band="medium",
                        detectability_band="low",
                        mitigation="Write disconfirming evidence thresholds and invite an outside reviewer.",
                        black_swan=False,
                    ),
                    RiskItem(
                        scenario_key=key,
                        risk_name="Support-system fatigue",
                        risk_type="common",
                        likelihood_band="medium",
                        severity_band="medium",
                        detectability_band="medium",
                        mitigation="Schedule explicit check-ins and protect recovery time.",
                        black_swan=False,
                    ),
                ]
            )
            if key == "stress":
                risks.append(
                    RiskItem(
                        scenario_key=key,
                        risk_name="External shock during low-liquidity window",
                        risk_type="black_swan",
                        likelihood_band="low",
                        severity_band="very_high",
                        detectability_band="low",
                        mitigation="Keep an emergency reserve and a re-entry plan before taking a one-way-door step.",
                        black_swan=True,
                    )
                )
        for flag in framed.high_stakes_flags:
            risks.append(
                RiskItem(
                    scenario_key="base",
                    risk_name=f"High-stakes boundary: {flag.domain}",
                    risk_type="safety",
                    likelihood_band="medium",
                    severity_band="high" if flag.severity != "block" else "very_high",
                    detectability_band="high",
                    mitigation=flag.recommended_boundary,
                    black_swan=False,
                )
            )
        return risks

    # Live Path using LLM
    system_prompt = (
        "You are the 'Black Swan Agent'. Your job is to identify execution, hidden, safety, and black swan risks associated with the user's decision paths, and provide concrete mitigations.\n"
        "Given the framed decision brief and scenario branches, evaluate potential failure points.\n"
        "For each risk item, specify:\n"
        "- scenario_key (must match one of the scenarios: 'optimistic', 'base', 'stress')\n"
        "- risk_name (name of the risk)\n"
        "- risk_type (must be one of: 'common', 'hidden', 'black_swan', 'safety', 'execution')\n"
        "- likelihood_band (must be one of: 'low', 'medium', 'high', 'very_high')\n"
        "- severity_band (must be one of: 'low', 'medium', 'high', 'very_high')\n"
        "- detectability_band (must be one of: 'low', 'medium', 'high', 'very_high')\n"
        "- mitigation (concrete action steps the user can take to hedge or prepare for this risk)\n"
        "- black_swan (boolean indicating if this is an extreme, low-probability but high-impact event)\n"
        "\nGenerate at least 1-2 risk items for each of the three scenarios.\n"
        "\nYou MUST respond with a JSON object matching this structure:\n"
        "{\n"
        "  \"risks\": [\n"
        "    {\n"
        "      \"scenario_key\": \"stress\",\n"
        "      \"risk_name\": \"...\",\n"
        "      \"risk_type\": \"black_swan\",\n"
        "      \"likelihood_band\": \"low\",\n"
        "      \"severity_band\": \"very_high\",\n"
        "      \"detectability_band\": \"low\",\n"
        "      \"mitigation\": \"...\",\n"
        "      \"black_swan\": true\n"
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

    result = model.complete_json(ModelRequest(system_prompt=system_prompt, user_payload=payload, schema_name="BlackSwanRisks"))
    risks: list[RiskItem] = []
    for item in result.get("risks", []):
        risks.append(
            RiskItem(
                scenario_key=item.get("scenario_key", "base"),
                risk_name=item.get("risk_name", "Unforeseen Risk"),
                risk_type=item.get("risk_type", "execution"),
                likelihood_band=item.get("likelihood_band", "medium"),
                severity_band=item.get("severity_band", "medium"),
                detectability_band=item.get("detectability_band", "medium"),
                mitigation=item.get("mitigation", ""),
                black_swan=item.get("black_swan", False),
            )
        )
    for flag in framed.high_stakes_flags:
        risks.append(
            RiskItem(
                scenario_key="base",
                risk_name=f"High-stakes boundary: {flag.domain}",
                risk_type="safety",
                likelihood_band="medium",
                severity_band="high" if flag.severity != "block" else "very_high",
                detectability_band="high",
                mitigation=flag.recommended_boundary,
                black_swan=False,
            )
        )
    return risks
