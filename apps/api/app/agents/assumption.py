from __future__ import annotations
from app.schemas import Citation, FramedDecision, GroundedClaim
from app.providers.model import ModelProvider, ModelRequest
from app.core.config import get_settings


def _ground_claims(claims: list[str], evidence: list[Citation]) -> list[GroundedClaim]:
    """Cite-or-abstain: tag each claim as grounded in a retrieved source, or
    unverified when no evidence supports it. A claim is grounded when it shares
    enough meaningful terms with a citation's title+snippet."""
    grounded: list[GroundedClaim] = []
    for claim in claims:
        claim_terms = {t.lower().strip(".,!?:;") for t in claim.split() if len(t) > 4}
        best: tuple[int, Citation | None] = (0, None)
        for cit in evidence:
            text = f"{cit.title} {cit.snippet}".lower()
            overlap = sum(1 for t in claim_terms if t in text)
            if overlap > best[0]:
                best = (overlap, cit)
        if best[0] >= 1 and best[1] is not None:
            grounded.append(GroundedClaim(text=claim, status="grounded",
                                          source=best[1].source, source_title=best[1].title))
        else:
            grounded.append(GroundedClaim(text=claim, status="unverified"))
    return grounded


def mine_assumptions(framed: FramedDecision, evidence: list[Citation], model: ModelProvider | None = None) -> tuple[list[str], list[GroundedClaim], list[str]]:
    """Surface hidden assumptions and data gaps from the decision brief and evidence bundle."""
    settings = get_settings()

    if settings.demo_mode or model is None or model.name == "mock":
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

        return assumptions, _ground_claims(assumptions, evidence), missing_info

    # Live Path using LLM
    system_prompt = (
        "You are the 'Assumption Miner Agent'. Your job is to analyze the framed decision context and evidence bundle to surface hidden assumptions and missing information (data gaps).\n"
        "Given the framed decision context and any retrieved evidence citations, extract:\n"
        "1. Core assumptions the user is implicitly making that need validation (minimum 3 assumptions).\n"
        "2. Critical missing information/data gaps the user should investigate before deciding (minimum 3 items).\n"
        "\nYou MUST respond with a JSON object matching this structure:\n"
        "{\n"
        "  \"assumptions\": [\"...\", \"...\"],\n"
        "  \"missing_information\": [\"...\", \"...\"]\n"
        "}"
    )

    payload = {
        "title": framed.title,
        "decision_type": framed.decision_type,
        "goals": framed.goals,
        "fears": framed.fears,
        "constraints": framed.constraints,
        "candidate_options": [opt.model_dump() for opt in framed.candidate_options],
        "evidence": [cit.model_dump() for cit in evidence],
    }

    result = model.complete_json(ModelRequest(system_prompt=system_prompt, user_payload=payload, schema_name="AssumptionMining"))
    assumptions = result.get("assumptions", [])
    return assumptions, _ground_claims(assumptions, evidence), result.get("missing_information", [])
