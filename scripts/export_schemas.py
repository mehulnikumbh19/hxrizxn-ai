from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api"))

from app.schemas import (  # noqa: E402
    AgentTraceView,
    DecisionIntake,
    DecisionMemo,
    ExperimentPlan,
    FramedDecision,
    OptionalityAssessment,
    RegretAssessment,
    RiskItem,
    SafetyFlag,
    ScenarioImpact,
    ScenarioSpec,
)


MODELS = [
    DecisionIntake,
    FramedDecision,
    ScenarioSpec,
    ScenarioImpact,
    RiskItem,
    RegretAssessment,
    OptionalityAssessment,
    ExperimentPlan,
    DecisionMemo,
    SafetyFlag,
    AgentTraceView,
]


def main() -> None:
    out = ROOT / "packages" / "types" / "schemas"
    out.mkdir(parents=True, exist_ok=True)
    for model in MODELS:
        (out / f"{model.__name__}.schema.json").write_text(
            json.dumps(model.model_json_schema(), indent=2),
            encoding="utf-8",
        )
    print(f"Exported {len(MODELS)} JSON schemas to {out}")


if __name__ == "__main__":
    main()

