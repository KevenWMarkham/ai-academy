"""academy-core — the scenario-chain runtime the whole academy runs on.

The unit of value is the *chain*, not the model: agents in named roles
(Assess → Classify → Quantify → Decide → ★HITL(16) → Act → Learn), grounded on
governed data, gated by a human where it matters, leaving a 14-field ledger row
per step, rolling up to KPIs a named persona owns.
"""

from academy_core.models import (
    ChainContext,
    ChainRequest,
    HitlMode,
    Kpi,
    Persona,
    Role,
    Scenario,
    ScenarioSpec,
    StageResult,
)
from academy_core.runtime import ChainRunner, GateOutcome, RunReport

__all__ = [
    "ChainContext",
    "ChainRequest",
    "ChainRunner",
    "GateOutcome",
    "HitlMode",
    "Kpi",
    "Persona",
    "Role",
    "RunReport",
    "Scenario",
    "ScenarioSpec",
    "StageResult",
]
