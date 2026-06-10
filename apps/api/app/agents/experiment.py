from __future__ import annotations

from app.schemas import ExperimentPlan, FramedDecision, RiskItem


def design_experiment(framed: FramedDecision, risks: list[RiskItem]) -> ExperimentPlan:
    top_risks = [risk.risk_name for risk in risks[:3]]
    plan_name = "30-day reversible HORIZON-X validation sprint"
    if framed.decision_type == "startup":
        steps = [
            "Interview 15 target users and record exact pain, budget, and current workaround.",
            "Build a landing page or concierge prototype and ask for a concrete commitment.",
            "Reserve two founder-energy blocks per week and track isolation, focus, and recovery.",
            "Run a weekly runway review using the emergency floor as a hard constraint.",
        ]
        success = [
            "At least 5 strong problem confirmations from target users.",
            "At least 2 concrete commitments, pilots, letters of intent, or paid trials.",
            "Energy remains sustainable for 3 of 4 weeks without sacrificing health or relationships.",
        ]
    else:
        steps = [
            "Define the irreversible part of the decision and delay only that part.",
            "Run three expert or peer conversations to test hidden assumptions.",
            "Simulate the financial and lifestyle week that the decision would create.",
            "Document evidence that would change the recommendation.",
        ]
        success = [
            "The main assumption survives outside feedback.",
            "The user can name what improves, what worsens, and what remains unknown.",
            "The next commitment is smaller than the original one-way-door move.",
        ]
    return ExperimentPlan(
        plan_name=plan_name,
        hypothesis=(
            "If the riskiest assumptions can survive a time-boxed test, the user can commit later with less regret exposure."
        ),
        duration_days=30,
        reversible=True,
        steps=steps,
        success_criteria=success,
        stop_conditions=[
            "Runway falls below the predefined safety floor.",
            "The strongest assumption receives repeated disconfirming evidence.",
            f"One of these top risks becomes active without mitigation: {', '.join(top_risks)}.",
        ],
        what_you_will_learn=[
            "Whether motivation survives contact with operational reality.",
            "Which branch of the scenario lattice is becoming more plausible.",
            "Whether commitment should increase, pause, or reverse.",
        ],
    )

