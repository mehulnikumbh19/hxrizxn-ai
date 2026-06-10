from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[3]
API_ROOT = ROOT / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

TEST_DB = API_ROOT / "test-hxrizxn.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"
os.environ["DEMO_MODE"] = "true"

from app.db.session import init_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def clean_db():
    if TEST_DB.exists():
        TEST_DB.unlink()
    init_db()
    yield
    if TEST_DB.exists():
        TEST_DB.unlink()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def sample_payload() -> dict:
    return {
        "title": "Quit job or test startup?",
        "decision_type": "startup",
        "raw_prompt": (
            "I'm a software engineer with 3 years of experience and 8 months of savings. "
            "Should I quit to start an AI startup, wait 6 months, or test part-time first?"
        ),
        "goals": ["Autonomy", "Learning velocity"],
        "fears": ["Burn rate", "Isolation"],
        "constraints": ["8 months savings"],
        "money_limit_months": 8,
        "time_horizon_months": 18,
    }

