from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import DecisionCase, DocumentDB, FinalRecommendationDB, ScenarioDB
from app.db.session import get_db
from app.schemas import AnalysisPackage, CaseCreateRequest, CaseResponse, DocumentResponse, ScenarioSpec
from app.services.orchestrator import HorizonXWorkflow
from app.services.reporting import render_markdown_report
from app.services.security import sanitize_retrieved_text, validate_upload_type

router = APIRouter(prefix="/api")

SAMPLE_PROMPT = (
    "I'm a software engineer with 3 years of experience. I have savings for 8 months. "
    "I want to quit my job and start an AI startup, but I'm worried about burn rate, isolation, "
    "and whether I'm romanticizing founder life. Should I quit now, wait 6 months, or test the idea part-time first?"
)


@router.get("/health")
def health() -> dict:
    settings = get_settings()
    return {
        "ok": True,
        "service": "hxrizxn-api",
        "demo_mode": settings.demo_mode,
        "foundry_iq_configured": settings.foundry_iq_configured,
    }


@router.post("/cases", response_model=CaseResponse)
def create_case(payload: CaseCreateRequest, db: Session = Depends(get_db)) -> DecisionCase:
    case = DecisionCase(
        title=payload.title or "Major decision simulation",
        decision_type=payload.decision_type,
        raw_prompt=payload.raw_prompt,
        structured_context_json={
            "goals": payload.goals,
            "fears": payload.fears,
            "constraints": payload.constraints,
            "money_limit_months": payload.money_limit_months,
            "dependencies": payload.dependencies,
        },
        time_horizon_months=payload.time_horizon_months,
        status="draft",
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


@router.get("/cases/{case_id}", response_model=CaseResponse)
def get_case(case_id: str, db: Session = Depends(get_db)) -> DecisionCase:
    case = db.get(DecisionCase, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.post("/cases/{case_id}/analyze", response_model=AnalysisPackage)
def analyze_case(case_id: str, db: Session = Depends(get_db)) -> AnalysisPackage:
    case = db.get(DecisionCase, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return HorizonXWorkflow().analyze_case(db, case)


@router.get("/cases/{case_id}/scenarios", response_model=list[ScenarioSpec])
def get_scenarios(case_id: str, db: Session = Depends(get_db)) -> list[ScenarioSpec]:
    rows = db.query(ScenarioDB).filter(ScenarioDB.case_id == case_id).all()
    return [
        ScenarioSpec(
            scenario_key=row.scenario_key,
            scenario_name=row.scenario_name,
            narrative=row.narrative,
            branching_logic=[],
            confidence_label=row.confidence_label,
            probability_band=row.probability_band,
            time_horizon=row.time_horizon,
            upside_score=row.upside_score,
            downside_score=row.downside_score,
            regret_score=row.regret_score,
            reversibility_score=row.reversibility_score,
            optionality_score=row.optionality_score,
            evidence=row.evidence_json,
        )
        for row in rows
    ]


@router.get("/cases/{case_id}/trace")
def get_trace(case_id: str, db: Session = Depends(get_db)) -> list[dict]:
    return [trace.model_dump() for trace in HorizonXWorkflow().trace_for_case(db, case_id)]


@router.post("/cases/{case_id}/documents", response_model=DocumentResponse)
async def upload_document(
    case_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> DocumentDB:
    case = db.get(DecisionCase, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    validate_upload_type(file.content_type or "application/octet-stream")
    settings = get_settings()
    upload_dir = Path(settings.upload_dir) / case_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "document.txt").suffix
    safe_name = f"{uuid4()}{suffix}"
    target = upload_dir / safe_name
    content = await file.read()
    if len(content) > 5_000_000:
        raise HTTPException(status_code=413, detail="File too large for MVP upload limit")
    target.write_bytes(content)
    text_status = "stored"
    metadata = {"original_filename": file.filename, "bytes": len(content)}
    if (file.content_type or "").startswith("text/"):
        metadata["preview"] = sanitize_retrieved_text(content.decode("utf-8", errors="ignore"))[:500]
        text_status = "extracted"
    doc = DocumentDB(
        case_id=case_id,
        filename=file.filename or safe_name,
        mime_type=file.content_type or "application/octet-stream",
        storage_uri=str(target),
        text_status=text_status,
        retrieval_status="mock-indexed",
        metadata_json=metadata,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/cases/{case_id}/report", response_class=PlainTextResponse)
def get_report(case_id: str, db: Session = Depends(get_db)) -> str:
    case = db.get(DecisionCase, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    if not db.query(FinalRecommendationDB).filter(FinalRecommendationDB.case_id == case_id).first():
        package = HorizonXWorkflow().analyze_case(db, case)
    else:
        package = HorizonXWorkflow().analyze_case(db, case)
    return render_markdown_report(package)


@router.get("/demo/scenarios", response_model=AnalysisPackage)
def get_demo_scenarios(db: Session = Depends(get_db)) -> AnalysisPackage:
    case = DecisionCase(
        title="Quit job or test the AI startup first?",
        decision_type="startup",
        raw_prompt=SAMPLE_PROMPT,
        structured_context_json={
            "goals": ["Founder autonomy", "Learning velocity", "Avoid irreversible regret"],
            "fears": ["Burn rate", "Isolation", "Romanticizing founder life"],
            "constraints": ["8 months savings", "3 years software engineering experience"],
            "money_limit_months": 8,
            "dependencies": ["Customer validation", "Support system", "Runway"],
        },
        time_horizon_months=18,
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return HorizonXWorkflow().analyze_case(db, case)

