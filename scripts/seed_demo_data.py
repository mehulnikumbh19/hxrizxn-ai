from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from app.db.models import DecisionCase  # noqa: E402
from app.db.session import SessionLocal, init_db  # noqa: E402


CASES = [
    (
        "Quit job or test the AI startup first?",
        "startup",
        "I'm a software engineer with 3 years of experience. I have savings for 8 months. I want to quit my job and start an AI startup, but I'm worried about burn rate, isolation, and whether I'm romanticizing founder life. Should I quit now, wait 6 months, or test the idea part-time first?",
    ),
    (
        "Move to another country?",
        "relocation",
        "Should I move to another country for a role that may accelerate my career, even though I am worried about visa rules, loneliness, and cost of living?",
    ),
    (
        "Pursue graduate school?",
        "graduate_school",
        "Should I pursue graduate school now, defer for a year, or test the field with a lower-cost course first?",
    ),
    (
        "Buy a house this year?",
        "home_purchase",
        "Should I buy a house this year or keep renting while my career and location are uncertain?",
    ),
    (
        "Switch careers into AI product?",
        "career",
        "Should I switch from cybersecurity operations into AI product management, stay in my current track, or run a portfolio experiment first?",
    ),
]


def main() -> None:
    init_db()
    with SessionLocal() as db:
        for title, decision_type, prompt in CASES:
            exists = db.query(DecisionCase).filter(DecisionCase.title == title).first()
            if exists:
                continue
            db.add(
                DecisionCase(
                    title=title,
                    decision_type=decision_type,
                    raw_prompt=prompt,
                    structured_context_json={
                        "goals": ["clarity", "optionality", "regret reduction"],
                        "fears": ["avoidable downside", "false confidence"],
                        "constraints": ["time", "money", "energy"],
                    },
                    time_horizon_months=18,
                    status="draft",
                )
            )
        db.commit()
    print(f"Seeded {len(CASES)} demo cases")


if __name__ == "__main__":
    main()

