"""API contract tests — what the M365 Copilot plugin depends on."""

from __future__ import annotations

import importlib

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(monkeypatch) -> TestClient:
    monkeypatch.delenv("ACADEMY_API_KEY", raising=False)
    from academy_api import main

    return TestClient(main.app)


def test_healthz(client) -> None:
    body = client.get("/healthz").json()
    assert body["status"] == "ok"


def test_list_scenarios_returns_all_nine(client) -> None:
    response = client.get("/scenarios")
    assert response.status_code == 200
    ids = [s["scenario_id"] for s in response.json()]
    assert ids == [f"hr-hrsd-0{n}" for n in range(1, 10)]


def test_get_scenario_detail(client) -> None:
    body = client.get("/scenarios/hr-hrsd-01").json()
    assert body["lead_agent"] == "Policy-QA"
    assert body["kpis"][0]["owner"].startswith("Sofia")
    assert client.get("/scenarios/nope").status_code == 404


def test_run_scenario_answers_with_gate_and_ledger(client) -> None:
    body = client.post("/runs", json={"scenario_id": "hr-hrsd-01"}).json()
    assert "[source: pto]" in body["answer"]
    assert body["gate"]["mode"] == "ZERO_TOUCH" and body["gate"]["approved"]
    gate_rows = [r for r in body["ledger"] if r["stage"] == "hitl-gate"]
    assert len(gate_rows) == 1 and gate_rows[0]["step"] == 16


def test_run_scenario_escalation_surfaces_route(client) -> None:
    body = client.post("/runs", json={"scenario_id": "hr-hrsd-08"}).json()
    assert body["gate"]["escalated"] is True
    assert "Payroll" in body["escalation_route"]


def test_run_scenario_custom_text(client) -> None:
    body = client.post(
        "/runs",
        json={"scenario_id": "hr-hrsd-09", "employee_id": "E1003",
              "text": "¿Cuántos días de vacaciones me quedan?"},
    ).json()
    assert "[en→es]" in body["answer"]


def test_api_key_enforced_when_configured(monkeypatch) -> None:
    monkeypatch.setenv("ACADEMY_API_KEY", "s3cret")
    from academy_api import main

    importlib.reload(main)  # re-read env-independent app is fine; the dep reads env per-call
    client = TestClient(main.app)
    assert client.get("/scenarios").status_code == 401
    assert client.get("/scenarios", headers={"X-Api-Key": "wrong"}).status_code == 401
    assert client.get("/scenarios", headers={"X-Api-Key": "s3cret"}).status_code == 200
