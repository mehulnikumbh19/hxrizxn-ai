from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
from time import perf_counter
from typing import Any, TypeVar

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.agents.composer import compose_memo
from app.agents.experiment import design_experiment
from app.agents.framing import frame_decision
from app.agents.optionality import score_optionality
from app.agents.regret import assess_regret
from app.agents.ripple import map_ripple_effects
from app.agents.risk import identify_risks
from app.agents.scenario_lattice import build_scenarios
from app.agents.verifier import verify_outputs
from app.core.config import get_settings
from app.db.models import (
    AgentRunDB,
    DecisionCase,
    DecisionOptionDB,
    ExperimentPlanDB,
    FinalRecommendationDB,
    ScenarioDB,
    ScenarioImpactDB,
    ScenarioRiskDB,
)
from app.providers.knowledge import get_knowledge_provider
from app.schemas import (
    AgentTraceView,
    AnalysisPackage,
    DecisionIntake,
    DecisionMemo,
    ExperimentPlan,
    FramedDecision,
    OptionalityAssessment,
    RegretAssessment,
    RiskItem,
    ScenarioImpact,
    ScenarioSpec,
)
from app.services.agent_framework_adapter import MicrosoftAgentFrameworkAdapter

T = TypeVar("T")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _summarize(value: Any) -> str:
    if hasattr(value, "model_dump"):
        data = value.model_dump()
    elif isinstance(value, list):
        data = [item.model_dump() if hasattr(item, "model_dump") else item for item in value[:3]]
    else:
        data = value
    text = str(data)
    return text[:260] + ("..." if len(text) > 260 else "")


def _run_agent(db: Session, case_id: str, agent_name: str, payload: dict, fn: Callable[[], T]) -> T:
    started = _utcnow()
    row = AgentRunDB(
        case_id=case_id,
        agent_name=agent_name,
        status="running",
        input_json=payload,
        output_json={},
        started_at=started,
    )
    db.add(row)
    db.commit()
    timer = perf_counter()
    try:
        output = fn()
        row.status = "completed"
        row.output_json = {"summary": _summarize(output)}
        return output
    except Exception as exc:
        row.status = "failed"
        row.error_text = str(exc)
        row.output_json = {"error": str(exc)}
        raise
    finally:
        row.completed_at = _utcnow()
        row.latency_ms = int((perf_counter() - timer) * 1000)
        db.add(row)
        db.commit()


class HorizonXWorkflow:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.knowledge = get_knowledge_provider(self.settings)
        self.framework = MicrosoftAgentFrameworkAdapter()

    def analyze_case(self, db: Session, case: DecisionCase) -> AnalysisPackage:
        self._clear_previous_outputs(db, case.id)
        intake = DecisionIntake(
            title=case.title,
            decision_type=case.decision_type,
            raw_prompt=case.raw_prompt,
            goals=case.structured_context_json.get("goals", []),
            fears=case.structured_context_json.get("fears", []),
            constraints=case.structured_context_json.get("constraints", []),
            money_limit_months=case.structured_context_json.get("money_limit_months"),
            time_horizon_months=case.time_horizon_months,
            dependencies=case.structured_context_json.get("dependencies", []),
        )
        framed = _run_agent(
            db,
            case.id,
            "Decision Framing Agent",
            {"horizon_x": "H/O", "framework": self.framework.metadata()},
            lambda: frame_decision(intake, case.id, self.knowledge),
        )
        self._persist_options(db, case.id, framed)
        scenarios = _run_agent(
            db,
            case.id,
            "Scenario Lattice Agent",
            {"horizon_x": "R", "framed_decision": framed.model_dump()},
            lambda: build_scenarios(framed, self.knowledge),
        )
        impacts = _run_agent(
            db,
            case.id,
            "Ripple Effects Agent",
            {"horizon_x": "I", "scenario_count": len(scenarios)},
            lambda: map_ripple_effects(framed, scenarios),
        )
        risks = _run_agent(
            db,
            case.id,
            "Risk and Black Swan Agent",
            {"horizon_x": "Z", "scenario_count": len(scenarios)},
            lambda: identify_risks(framed, scenarios),
        )
        optionality = _run_agent(
            db,
            case.id,
            "Optionality and Reversibility Agent",
            {"horizon_x": "O", "scenario_count": len(scenarios)},
            lambda: score_optionality(framed, scenarios),
        )
        regret = _run_agent(
            db,
            case.id,
            "Regret and Future Self Agent",
            {"horizon_x": "N/X", "scenario_count": len(scenarios)},
            lambda: assess_regret(framed, scenarios),
        )
        experiment = _run_agent(
            db,
            case.id,
            "Experiment Design Agent",
            {"horizon_x": "N", "risk_count": len(risks)},
            lambda: design_experiment(framed, risks),
        )
        verification = _run_agent(
            db,
            case.id,
            "Verifier and Safety Agent",
            {"horizon_x": "X", "safety_flags": [flag.model_dump() for flag in framed.high_stakes_flags]},
            lambda: verify_outputs(framed, scenarios, impacts, risks, experiment),
        )
        if not verification.approved:
            framed.missing_information.extend(verification["confidence_notes"])
        memo = _run_agent(
            db,
            case.id,
            "Recommendation Composer Agent",
            {"horizon_x": "X", "verification": dict(verification)},
            lambda: compose_memo(framed, scenarios, risks, optionality, regret, experiment),
        )
        self._persist_analysis(db, case, scenarios, impacts, risks, experiment, memo)
        trace = self.trace_for_case(db, case.id)
        return AnalysisPackage(
            case_id=case.id,
            framed_decision=framed,
            scenarios=scenarios,
            impacts=impacts,
            risks=risks,
            optionality=optionality,
            regret=regret,
            experiment_plan=experiment,
            safety_flags=framed.high_stakes_flags,
            memo=memo,
            trace=trace,
        )

    def trace_for_case(self, db: Session, case_id: str) -> list[AgentTraceView]:
        rows = (
            db.query(AgentRunDB)
            .filter(AgentRunDB.case_id == case_id)
            .order_by(AgentRunDB.started_at.asc())
            .all()
        )
        return [
            AgentTraceView(
                agent_name=row.agent_name,
                status=row.status,
                input_summary=_summarize(row.input_json),
                output_summary=_summarize(row.output_json),
                started_at=row.started_at,
                completed_at=row.completed_at,
                latency_ms=row.latency_ms,
            )
            for row in rows
        ]

    def _clear_previous_outputs(self, db: Session, case_id: str) -> None:
        for model in [
            ScenarioImpactDB,
            ScenarioRiskDB,
            ScenarioDB,
            DecisionOptionDB,
            ExperimentPlanDB,
            FinalRecommendationDB,
            AgentRunDB,
        ]:
            if model in {ScenarioImpactDB, ScenarioRiskDB}:
                continue
            db.execute(delete(model).where(model.case_id == case_id))
        db.commit()

    def _persist_options(self, db: Session, case_id: str, framed: FramedDecision) -> None:
        for option in framed.candidate_options:
            db.add(
                DecisionOptionDB(
                    case_id=case_id,
                    option_key=option.option_key,
                    label=option.label,
                    description=option.description,
                )
            )
        db.commit()

    def _persist_analysis(
        self,
        db: Session,
        case: DecisionCase,
        scenarios: list[ScenarioSpec],
        impacts: list[ScenarioImpact],
        risks: list[RiskItem],
        experiment: ExperimentPlan,
        memo: DecisionMemo,
    ) -> None:
        scenario_rows: dict[str, ScenarioDB] = {}
        for scenario in scenarios:
            row = ScenarioDB(
                case_id=case.id,
                scenario_key=scenario.scenario_key,
                scenario_name=scenario.scenario_name,
                narrative=scenario.narrative,
                confidence_label=scenario.confidence_label,
                probability_band=scenario.probability_band,
                time_horizon=scenario.time_horizon,
                upside_score=scenario.upside_score,
                downside_score=scenario.downside_score,
                regret_score=scenario.regret_score,
                reversibility_score=scenario.reversibility_score,
                optionality_score=scenario.optionality_score,
                evidence_json=[citation.model_dump() for citation in scenario.evidence],
            )
            db.add(row)
            db.flush()
            scenario_rows[scenario.scenario_key] = row
        for impact in impacts:
            scenario_row = scenario_rows[impact.scenario_key]
            db.add(
                ScenarioImpactDB(
                    scenario_id=scenario_row.id,
                    domain=impact.domain,
                    order_level=impact.order_level,
                    impact_direction=impact.impact_direction,
                    severity=impact.severity,
                    explanation=impact.explanation,
                )
            )
        for risk in risks:
            if risk.scenario_key not in scenario_rows:
                continue
            scenario_row = scenario_rows[risk.scenario_key]
            db.add(
                ScenarioRiskDB(
                    scenario_id=scenario_row.id,
                    risk_name=risk.risk_name,
                    risk_type=risk.risk_type,
                    likelihood_band=risk.likelihood_band,
                    severity_band=risk.severity_band,
                    detectability_band=risk.detectability_band,
                    mitigation=risk.mitigation,
                    black_swan=risk.black_swan,
                )
            )
        db.add(
            ExperimentPlanDB(
                case_id=case.id,
                plan_name=experiment.plan_name,
                hypothesis=experiment.hypothesis,
                duration_days=experiment.duration_days,
                reversible=experiment.reversible,
                steps_json=experiment.steps,
                success_criteria_json=experiment.success_criteria,
                stop_conditions_json=experiment.stop_conditions,
            )
        )
        db.add(
            FinalRecommendationDB(
                case_id=case.id,
                recommendation_summary=memo.recommendation_summary,
                rationale=memo.rationale,
                uncertainty_notes=memo.uncertainty_notes,
                disclaimers=memo.disclaimers,
            )
        )
        case.status = "analyzed"
        case.updated_at = _utcnow()
        db.add(case)
        db.commit()

