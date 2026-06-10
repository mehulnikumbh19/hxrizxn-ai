from __future__ import annotations

from app.providers.knowledge import KnowledgeProvider, RetrievalQuery
from app.schemas import FramedDecision, ScenarioSpec


def build_scenarios(framed: FramedDecision, knowledge: KnowledgeProvider) -> list[ScenarioSpec]:
    evidence = knowledge.retrieve(
        RetrievalQuery(
            case_id=framed.case_id,
            query=f"{framed.decision_type} scenario planning reversibility regret",
            decision_type=framed.decision_type,
            top_k=3,
        )
    )
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

