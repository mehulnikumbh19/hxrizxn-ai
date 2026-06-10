from __future__ import annotations

from app.agents.safety import detect_safety_flags
from app.providers.knowledge import KnowledgeProvider, RetrievalQuery
from app.schemas import DecisionIntake, DecisionOption, FramedDecision


def _contains_any(text: str, words: list[str]) -> bool:
    lowered = text.lower()
    return any(word in lowered for word in words)


def frame_decision(intake: DecisionIntake, case_id: str, knowledge: KnowledgeProvider) -> FramedDecision:
    prompt = intake.raw_prompt
    decision_type = intake.decision_type
    if _contains_any(prompt, ["quit", "startup", "founder"]):
        decision_type = "startup"
        options = [
            DecisionOption(
                option_key="quit_now",
                label="Quit now",
                description="Leave the current job and pursue the AI startup full time immediately.",
            ),
            DecisionOption(
                option_key="wait_six_months",
                label="Wait 6 months",
                description="Keep income while saving more runway and validating the startup thesis.",
            ),
            DecisionOption(
                option_key="part_time_test",
                label="Test part-time first",
                description="Run a constrained startup validation sprint before resigning.",
            ),
        ]
    elif _contains_any(prompt, ["move", "country", "visa", "relocat"]):
        decision_type = "relocation"
        options = [
            DecisionOption(option_key="move_now", label="Move now", description="Commit to the relocation path."),
            DecisionOption(option_key="delay", label="Delay", description="Prepare documents, savings, and support first."),
            DecisionOption(option_key="trial", label="Run a trial stay", description="Test the location before a full move."),
        ]
    elif _contains_any(prompt, ["grad", "school", "degree", "mba", "master"]):
        decision_type = "graduate_school"
        options = [
            DecisionOption(option_key="enroll", label="Enroll", description="Commit to the program now."),
            DecisionOption(option_key="defer", label="Defer", description="Delay while testing career alternatives."),
            DecisionOption(option_key="course_pilot", label="Course pilot", description="Take a low-cost class first."),
        ]
    elif _contains_any(prompt, ["house", "mortgage", "home"]):
        decision_type = "home_purchase"
        options = [
            DecisionOption(option_key="buy_now", label="Buy now", description="Purchase within the current market window."),
            DecisionOption(option_key="rent_wait", label="Rent and wait", description="Preserve mobility and cash."),
            DecisionOption(option_key="smaller_buy", label="Buy smaller", description="Reduce lock-in with a lower-risk purchase."),
        ]
    else:
        options = [
            DecisionOption(option_key="commit", label="Commit", description="Take the main path now."),
            DecisionOption(option_key="delay", label="Delay", description="Wait and gather more evidence."),
            DecisionOption(option_key="experiment", label="Experiment", description="Run a reversible test first."),
        ]

    goals = intake.goals or [
        "Make a high-agency choice without creating avoidable long-term regret.",
        "Preserve enough runway and energy to keep learning after the decision.",
    ]
    fears = intake.fears or [
        "Romanticizing the upside while underestimating execution cost.",
        "Losing optionality through a premature irreversible move.",
    ]
    constraints = intake.constraints or [
        "Runway, time, relationships, location, and credibility must be protected.",
    ]
    assumptions = [
        "The user values autonomy but does not want reckless downside exposure.",
        "The highest-value unknowns can be reduced through a time-boxed experiment.",
        "Scenario outputs are plausible simulations, not predictions.",
    ]
    if intake.money_limit_months:
        assumptions.append(f"Available runway is approximately {intake.money_limit_months} months.")
    missing = [
        "Precise monthly burn and emergency floor.",
        "Outside validation from customers, employers, schools, or domain experts.",
        "Personal support system and recovery plan if the path fails.",
    ]
    evidence = knowledge.retrieve(
        RetrievalQuery(case_id=case_id, query=prompt, decision_type=decision_type, top_k=4)
    )
    title = intake.title or _infer_title(prompt, decision_type)
    return FramedDecision(
        case_id=case_id,
        title=title,
        decision_type=decision_type,
        goals=goals,
        fears=fears,
        constraints=constraints,
        assumptions=assumptions,
        missing_information=missing,
        candidate_options=options,
        high_stakes_flags=detect_safety_flags(prompt),
        evidence=evidence,
    )


def _infer_title(prompt: str, decision_type: str) -> str:
    clean = " ".join(prompt.strip().split())
    if len(clean) <= 80:
        return clean
    labels = {
        "startup": "Quit job or test the startup first?",
        "relocation": "Move now or preserve relocation optionality?",
        "graduate_school": "Pursue graduate school or test alternatives?",
        "home_purchase": "Buy a house now or preserve flexibility?",
    }
    return labels.get(decision_type, "Major decision simulation")

