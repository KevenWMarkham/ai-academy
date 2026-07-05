"""Shared models for the AI Academy scenario-chain runtime."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Role(StrEnum):
    """The six agent roles of the executable chain segment (canonical W2 pilot wave)."""

    ASSESS = "assess"
    CLASSIFY = "classify"
    QUANTIFY = "quantify"
    DECIDE = "decide"
    ACT = "act"
    LEARN = "learn"


#: Which canonical 24-step number each role executes as (see docs/01-scenario-chains.md).
#: DECIDE composes the proposal that the step-16 HITL gate approves; ACT only runs after it.
ROLE_CANONICAL_STEP: dict[Role, int] = {
    Role.ASSESS: 13,
    Role.CLASSIFY: 14,
    Role.QUANTIFY: 15,
    Role.DECIDE: 16,
    Role.ACT: 17,
    Role.LEARN: 23,
}


class HitlMode(StrEnum):
    """How much human attention the step-16 gate demands."""

    ZERO_TOUCH = "ZERO_TOUCH"  # auto-approved; every step still fully evidenced in the ledger
    ACK_ONLY = "ACK_ONLY"  # a human acknowledges the proposal; they do not redesign the work
    ESCALATION = "ESCALATION"  # auto unless confidence drops below threshold → route to a human
    HITL = "HITL"  # hard gate: a named human must approve before ACT runs


@dataclass(frozen=True)
class Kpi:
    """A KPI a named persona owns. Baselines/targets are synthetic reference figures."""

    name: str
    owner: str
    baseline: str
    target: str
    driver: str  # how the chain moves it


@dataclass(frozen=True)
class Persona:
    name: str
    role: str
    home: str  # where they sit in HR
    surface: str  # the only way they meet the platform (Copilot in Teams, Power BI, …)


@dataclass
class ChainRequest:
    """What the persona typed (or the event that fired) to start the chain — step 11."""

    employee_id: str
    text: str
    locale: str = "en-US"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class StageResult:
    """What one role produced. ``confidence`` on DECIDE feeds the step-16 gate."""

    role: Role
    summary: str
    data: dict[str, Any] = field(default_factory=dict)
    confidence: float | None = None


@dataclass
class ChainContext:
    """Mutable state threaded through the chain — one run, one context."""

    request: ChainRequest
    services: Any  # a ServiceHub (typed loosely so core has zero dependencies)
    employee: dict[str, Any] = field(default_factory=dict)
    state: dict[str, Any] = field(default_factory=dict)
    results: dict[Role, StageResult] = field(default_factory=dict)


Handler = Callable[[ChainContext], StageResult]


@dataclass(frozen=True)
class ScenarioSpec:
    """Everything a scenario declares about itself — the teaching contract."""

    scenario_id: str  # e.g. "hr-hrsd-01"
    name: str
    tagline: str
    service: str  # productized service group, e.g. "HR-HRSD-01 · Policy Q&A Copilot"
    chain_focus: str  # the role(s) that do the heavy lifting, e.g. "Classify"
    hitl_mode: HitlMode
    lead_agent: str
    personas: tuple[str, ...]
    kpis: tuple[Kpi, ...]
    azure_services: tuple[str, ...]
    data_tools: tuple[str, ...]
    sample_text: str  # a request that demos this scenario with no arguments
    sample_employee: str = "E1001"
    area: str = "HR Service Delivery (Tier-0)"
    maf_pattern: str = "Sequential"


@dataclass(frozen=True)
class Scenario:
    """A spec plus the stage handlers that implement it."""

    spec: ScenarioSpec
    handlers: dict[Role, Handler]
