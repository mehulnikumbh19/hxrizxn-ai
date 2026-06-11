from __future__ import annotations
from app.schemas import ExperimentPlan, FramedDecision, RiskItem
from app.providers.model import ModelProvider, ModelRequest
from app.core.config import get_settings


def design_experiment(framed: FramedDecision, risks: list[RiskItem], model: ModelProvider | None = None) -> ExperimentPlan:
    settings = get_settings()

    if settings.demo_mode or model is None or model.name == "mock":
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

    # Live Path using LLM
    system_prompt = (
        "You are the 'Experiment Design Agent'. Your job is to design a concrete, low-cost, and highly reversible experiment (or validation sprint) the user can run before making their decision.\n"
        "The experiment must aim to gather data on the user's primary assumptions and hedge against the most severe risks.\n"
        "Given the framed decision brief and identified risks, generate:\n"
        "- plan_name (a descriptive name for the experiment)\n"
        "- hypothesis (the core hypothesis being tested)\n"
        "- duration_days (an integer from 1 to 180, typically 30 or 60 days)\n"
        "- reversible (boolean, should be true since it is an experiment)\n"
        "- steps (list of 3-5 concrete step-by-step actions to execute the experiment)\n"
        "- success_criteria (list of 2-3 specific indicators that show the experiment succeeded)\n"
        "- stop_conditions (list of 2-3 specific conditions under which the user should stop/abort the experiment)\n"
        "- what_you_will_learn (list of 2-3 specific insights/learnings the user will gain)\n"
        "\nYou MUST respond with a JSON object matching this structure:\n"
        "{\n"
        "  \"plan_name\": \"...\",\n"
        "  \"hypothesis\": \"...\",\n"
        "  \"duration_days\": 30,\n"
        "  \"reversible\": true,\n"
        "  \"steps\": [\"...\", \"...\"],\n"
        "  \"success_criteria\": [\"...\", \"...\"],\n"
        "  \"stop_conditions\": [\"...\", \"...\"],\n"
        "  \"what_you_will_learn\": [\"...\", \"...\"]\n"
        "}"
    )

    payload = {
        "title": framed.title,
        "decision_type": framed.decision_type,
        "goals": framed.goals,
        "fears": framed.fears,
        "constraints": framed.constraints,
        "candidate_options": [opt.model_dump() for opt in framed.candidate_options],
        "risks": [risk.model_dump() for risk in risks],
    }

    result = model.complete_json(ModelRequest(system_prompt=system_prompt, user_payload=payload, schema_name="ExperimentDesign"))
    return ExperimentPlan(
        plan_name=result.get("plan_name", "Reversible sprint"),
        hypothesis=result.get("hypothesis", ""),
        duration_days=result.get("duration_days", 30),
        reversible=result.get("reversible", True),
        steps=result.get("steps", []),
        success_criteria=result.get("success_criteria", []),
        stop_conditions=result.get("stop_conditions", []),
        what_you_will_learn=result.get("what_you_will_learn", []),
    )
