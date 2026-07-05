"""Runtime contract tests — the invariants every scenario must keep."""

from __future__ import annotations

import dataclasses

import pytest

import academy_hrsd  # noqa: F401  (import = scenario registration)
from academy_core.chain import CANONICAL_24_STEP_CHAIN, HITL_GATE_STEP
from academy_core.ledger import LEDGER_FIELD_COUNT
from academy_core.models import HitlMode
from academy_core.registry import all_scenarios, get
from academy_core.runtime import ChainRunner
from academy_services.hub import ServiceHub


@pytest.fixture(scope="module")
def hub() -> ServiceHub:
    return ServiceHub(runtime="mock")


def test_all_nine_scenarios_registered() -> None:
    ids = [s.spec.scenario_id for s in all_scenarios()]
    assert ids == [f"hr-hrsd-0{n}" for n in range(1, 10)]


def test_canonical_chain_shape() -> None:
    assert len(CANONICAL_24_STEP_CHAIN) == 24
    assert [s["step"] for s in CANONICAL_24_STEP_CHAIN] == list(range(1, 25))
    assert CANONICAL_24_STEP_CHAIN[HITL_GATE_STEP - 1]["kind"] == "hitl"


def test_ledger_row_has_exactly_14_fields() -> None:
    assert LEDGER_FIELD_COUNT == 14


@pytest.mark.parametrize("scenario", all_scenarios(), ids=lambda s: s.spec.scenario_id)
def test_scenario_runs_end_to_end(scenario, hub) -> None:
    report = ChainRunner(hub).run(scenario)
    assert report.answer, "every run must produce an answer for the persona"
    # Exactly one HITL gate row, at canonical step 16.
    gate_rows = [r for r in report.ledger.rows if r.stage == "hitl-gate"]
    assert len(gate_rows) == 1
    assert gate_rows[0].step == HITL_GATE_STEP
    # The trigger, orchestrate and KPI-rollup steps are always evidenced.
    stages = {r.stage for r in report.ledger.rows}
    assert {"trigger", "orchestrate", "kpi-rollup"} <= stages
    # Every row carries all 14 fields, populated.
    for row in report.ledger.rows:
        assert len(dataclasses.asdict(row)) == 14


@pytest.mark.parametrize("scenario", all_scenarios(), ids=lambda s: s.spec.scenario_id)
def test_zero_touch_and_ack_scenarios_act(scenario, hub) -> None:
    if scenario.spec.hitl_mode not in (HitlMode.ZERO_TOUCH, HitlMode.ACK_ONLY):
        pytest.skip("gate behaviour covered separately")
    report = ChainRunner(hub).run(scenario)
    assert report.gate is not None and report.gate.approved
    acted = [r for r in report.ledger.rows if r.stage == "act"]
    assert acted and acted[0].outcome == "ok"


def test_escalation_gate_fires_on_low_confidence(hub) -> None:
    report = ChainRunner(hub).run(get("hr-hrsd-08"))
    assert report.gate is not None
    assert report.gate.escalated, "the garnishment sample must fall below the threshold"
    assert report.escalation_route and "Payroll" in report.escalation_route
    assert "[escalated]" in report.answer


def test_deflection_resolves_when_kb_covers_it(hub) -> None:
    from academy_core.models import ChainRequest

    report = ChainRunner(hub).run(
        get("hr-hrsd-08"),
        ChainRequest("E1001", "How many unused PTO days can I carry over into next year?"),
    )
    assert report.gate is not None and report.gate.approved and not report.gate.escalated
