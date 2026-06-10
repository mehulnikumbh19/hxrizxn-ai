from __future__ import annotations

from app.schemas import FramedDecision, RiskItem, ScenarioSpec


def identify_risks(framed: FramedDecision, scenarios: list[ScenarioSpec]) -> list[RiskItem]:
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

