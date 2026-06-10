from __future__ import annotations

from app.schemas import AnalysisPackage


def render_markdown_report(package: AnalysisPackage) -> str:
    lines = [
        f"# Hxrizxn AI Decision Memo: {package.framed_decision.title}",
        "",
        "## HORIZON-X Recommendation",
        package.memo.recommendation_summary,
        "",
        "## Why",
        package.memo.rationale,
        "",
        "## Scenario Lattice",
    ]
    for scenario in package.scenarios:
        lines.extend(
            [
                f"### {scenario.scenario_name}",
                scenario.narrative,
                f"- Probability band: {scenario.probability_band}",
                f"- Reversibility: {scenario.reversibility_score}/100",
                f"- Optionality: {scenario.optionality_score}/100",
                f"- Regret exposure: {scenario.regret_score}/100",
                "",
            ]
        )
    lines.extend(
        [
            "## Safer Experiment",
            package.experiment_plan.plan_name,
            package.experiment_plan.hypothesis,
            "",
            "## Stop Conditions",
            *[f"- {condition}" for condition in package.experiment_plan.stop_conditions],
            "",
            "## Unknowns",
            package.memo.uncertainty_notes,
            "",
            "## Disclaimer",
            package.memo.disclaimers,
        ]
    )
    return "\n".join(lines)

