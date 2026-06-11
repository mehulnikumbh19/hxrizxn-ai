from __future__ import annotations

import json

import pytest

from app.db.models import AgentRunDB, DecisionCase
from app.db.session import SessionLocal
from app.providers.model import ModelOutputError, _request_json_with_retry
from app.services.orchestrator import _run_agent


def _make_case(db) -> str:
    case = DecisionCase(
        title="t",
        decision_type="startup",
        raw_prompt="p",
        structured_context_json={},
        time_horizon_months=12,
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return case.id


def _failing():
    raise ValueError("boom")


def test_run_agent_degrades_to_fallback_on_failure():
    db = SessionLocal()
    try:
        case_id = _make_case(db)
        result = _run_agent(db, case_id, "Flaky Agent", {}, _failing, fallback=lambda: "safe")
        assert result == "safe"
        row = db.query(AgentRunDB).filter(AgentRunDB.case_id == case_id).first()
        assert row.status == "degraded"
        assert "boom" in row.error_text
    finally:
        db.close()


def test_run_agent_reraises_without_fallback():
    db = SessionLocal()
    try:
        case_id = _make_case(db)
        with pytest.raises(ValueError):
            _run_agent(db, case_id, "Critical Agent", {}, _failing)
        row = db.query(AgentRunDB).filter(AgentRunDB.case_id == case_id).first()
        assert row.status == "failed"
    finally:
        db.close()


def test_run_agent_marks_failed_when_fallback_also_fails():
    db = SessionLocal()
    try:
        case_id = _make_case(db)

        def bad_fallback():
            raise RuntimeError("secondary")

        with pytest.raises(RuntimeError):
            _run_agent(db, case_id, "Doomed Agent", {}, _failing, fallback=bad_fallback)
        row = db.query(AgentRunDB).filter(AgentRunDB.case_id == case_id).first()
        assert row.status == "failed"
        assert "secondary" in row.error_text
    finally:
        db.close()


class _FakeResponse:
    def __init__(self, content: str):
        self._content = content

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return {"choices": [{"message": {"content": self._content}}]}


def test_request_json_with_retry_raises_model_output_error_on_bad_json():
    calls = {"n": 0}

    def do_request():
        calls["n"] += 1
        return _FakeResponse("not json at all")

    with pytest.raises(ModelOutputError):
        _request_json_with_retry(do_request, attempts=2)
    assert calls["n"] == 2  # retried once before giving up


def test_request_json_with_retry_recovers_on_second_attempt():
    responses = [_FakeResponse("oops"), _FakeResponse(json.dumps({"ok": True}))]

    def do_request():
        return responses.pop(0)

    assert _request_json_with_retry(do_request, attempts=2) == {"ok": True}
