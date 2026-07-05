"""Scenario-specific behaviour — the teaching moments each brief promises."""

from __future__ import annotations

import pytest

import academy_hrsd  # noqa: F401  (import = scenario registration)
from academy_core.models import ChainRequest, HitlMode
from academy_core.registry import get
from academy_core.runtime import ChainRunner
from academy_services.hub import ServiceHub


@pytest.fixture(scope="module")
def hub() -> ServiceHub:
    return ServiceHub(runtime="mock")


@pytest.fixture(scope="module")
def runner(hub) -> ChainRunner:
    return ChainRunner(hub)


def test_policy_qa_answer_is_cited_and_personal(runner) -> None:
    report = runner.run(get("hr-hrsd-01"))
    assert "[source: pto]" in report.answer
    assert "14.5" in report.answer  # Raj's own balance, from gold_hr_worker_v2
    assert "US-CA" in report.answer  # his jurisdiction rider surfaced


def test_status_lookup_finds_the_right_case(runner) -> None:
    report = runner.run(get("hr-hrsd-02"))
    assert "HRC-20431" in report.answer
    assert "Manager approval" in report.answer


def test_kb_search_ranks_remote_work_policy_first(runner) -> None:
    report = runner.run(get("hr-hrsd-03"))
    assert "Remote & Hybrid Work Policy" in report.answer.splitlines()[2]


def test_life_event_plan_is_deadline_ordered(runner) -> None:
    report = runner.run(get("hr-hrsd-04"))
    assert "within 30 days" in report.answer
    assert report.answer.index("30 days") < report.answer.index("31 days")


def test_leave_guidance_includes_ca_pfl_for_california_employee(runner) -> None:
    report = runner.run(get("hr-hrsd-05"))
    assert "CA Paid Family Leave" in report.answer
    assert "6.0 sick days" in report.answer or "6 sick days" in report.answer


def test_doc_generation_renders_a_complete_letter(runner) -> None:
    report = runner.run(get("hr-hrsd-06"))
    assert "Employment Verification Letter" in report.answer
    assert "Raj Patel" in report.answer
    assert "{" not in report.answer.split("---")[-1] or "{name}" not in report.answer
    assert report.gate is not None and report.gate.mode is HitlMode.ACK_ONLY
    assert "requesting employee" in report.gate.actor


def test_data_correction_detects_address_and_routes_to_data_team(runner) -> None:
    report = runner.run(get("hr-hrsd-07"))
    assert "address" in report.answer
    assert "HR Data Services" in report.answer
    assert "2189 Alameda Ave" in report.answer  # the PII entity became the proposed value


def test_multilingual_answers_in_the_asker_language(runner) -> None:
    report = runner.run(get("hr-hrsd-09"))
    # Mock translation is a tagged pass-through: the en→es hop must be visible.
    assert "[en→es]" in report.answer
    assert "9.0" in report.answer  # Lucía's balance


def test_multilingual_passes_english_straight_through(runner) -> None:
    report = runner.run(
        get("hr-hrsd-09"), ChainRequest("E1001", "How many PTO days do I have left?")
    )
    assert "[en→" not in report.answer
    assert "14.5" in report.answer
