from __future__ import annotations


def test_create_analyze_trace_and_report(client, sample_payload):
    created = client.post("/api/cases", json=sample_payload)
    assert created.status_code == 200
    case_id = created.json()["id"]

    analyzed = client.post(f"/api/cases/{case_id}/analyze")
    assert analyzed.status_code == 200
    body = analyzed.json()
    assert body["framed_decision"]["decision_type"] == "startup"
    assert len(body["scenarios"]) == 3
    assert {scenario["scenario_key"] for scenario in body["scenarios"]} == {
        "optimistic",
        "base",
        "stress",
    }
    assert body["experiment_plan"]["reversible"] is True
    assert "HORIZON-X" in body["experiment_plan"]["plan_name"]

    trace = client.get(f"/api/cases/{case_id}/trace")
    assert trace.status_code == 200
    assert len(trace.json()) >= 9

    report = client.get(f"/api/cases/{case_id}/report")
    assert report.status_code == 200
    assert "Hxrizxn AI Decision Memo" in report.text
    assert "HORIZON-X" in report.text


def test_demo_scenarios_endpoint(client):
    response = client.get("/api/demo/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert data["memo"]["recommendation_summary"].startswith("Proceed via experiment")
    assert data["scenarios"][1]["reversibility_score"] >= 80

