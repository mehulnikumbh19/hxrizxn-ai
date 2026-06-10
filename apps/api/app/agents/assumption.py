from __future__ import annotations

from app.schemas import Citation, FramedDecision


def mine_assumptions(framed: FramedDecision, evidence: list[Citation]) -> tuple[list[str], list[str]]:
    """Surface hidden assumptions and data gaps from the decision brief and evidence bundle."""
    assumptions = [
        "The user values autonomy but does not want reckless downside exposure.",
        "The highest-value unknowns can be reduced through a time-boxed experiment.",
        "Scenario outputs are plausible simulations, not predictions.",
    ]

    missing_info = [
        "Precise monthly burn and emergency floor.",
        "Outside validation from customers, employers, schools, or domain experts.",
        "Personal support system and recovery plan if the path fails.",
    ]

    if framed.decision_type == "startup":
        assumptions.append("Starting full-time immediately requires at least 12-18 months of burn runway.")
        missing_info.append("Commitment level of potential co-founders or first partners.")
    elif framed.decision_type == "relocation":
        assumptions.append("Relocation will accelerate career growth more than local alternatives.")
        missing_info.append("Detailed cost-of-living comparison and local tax implications.")
    elif framed.decision_type == "graduate_school":
        assumptions.append("A formal degree provides better signaling than equivalent portfolio projects.")
        missing_info.append("Post-graduation placement rates and median starting salaries for the program.")
    elif framed.decision_type == "home_purchase":
        assumptions.append("The purchase location remains desirable over a 5-10 year time horizon.")
        missing_info.append("Home inspection details and long-term HOA/maintenance costs.")

    for citation in evidence:
        if "burn" in citation.snippet.lower() or "runway" in citation.snippet.lower():
            if "Runway is the primary survival metric under high career uncertainty." not in assumptions:
                assumptions.append("Runway is the primary survival metric under high career uncertainty.")

    return assumptions, missing_info
