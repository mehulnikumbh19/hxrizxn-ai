from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from app.db.models import DecisionCase  # noqa: E402
from app.db.session import SessionLocal, init_db  # noqa: E402
from app.services.orchestrator import HorizonXWorkflow  # noqa: E402


def score_package(package, must_include: list[str]) -> dict:
    text = json.dumps(package.model_dump(), default=str).lower()
    scenario_keys = {scenario.scenario_key for scenario in package.scenarios}
    return {
        "structure_completeness": int(len(package.scenarios) == 3 and len(package.trace) >= 9),
        "scenario_diversity": int(scenario_keys == {"optimistic", "base", "stress"}),
        "second_order_coverage": int(any(impact.order_level >= 2 for impact in package.impacts)),
        "recommendation_usefulness": int("experiment" in package.memo.recommendation_summary.lower()),
        "safety_compliance": int("licensed professional" in package.memo.disclaimers.lower()),
        "scenario_memo_consistency": int("optionality" in package.memo.rationale.lower()),
        "citation_presence": int(bool(package.memo.citations)),
        "keyword_coverage": sum(1 for term in must_include if term.lower() in text),
    }


def main() -> None:
    init_db()
    golden = json.loads((ROOT / "evals" / "golden_cases.json").read_text(encoding="utf-8"))
    workflow = HorizonXWorkflow()
    results = []
    with SessionLocal() as db:
        for item in golden:
            case = DecisionCase(
                title=item["id"],
                decision_type=item["decision_type"],
                raw_prompt=item["prompt"],
                structured_context_json={},
                time_horizon_months=18,
            )
            db.add(case)
            db.commit()
            db.refresh(case)
            package = workflow.analyze_case(db, case)
            scores = score_package(package, item["must_include"])
            results.append({"id": item["id"], "scores": scores, "total": sum(scores.values())})
    out = ROOT / "evals" / "latest-results.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps({"cases": len(results), "output": str(out), "average": sum(r["total"] for r in results) / len(results)}, indent=2))


if __name__ == "__main__":
    main()

