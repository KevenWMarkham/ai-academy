"""ChainRunner — executes a scenario's six-role chain segment with one gate at step 16.

This is the whole engine (~200 lines). Students should read it top to bottom:
trigger → orchestrate → ASSESS → CLASSIFY → QUANTIFY → DECIDE → ★HITL gate →
ACT (only if approved) → LEARN → KPI rollup. Every executed step writes one
14-field ledger row.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from academy_core.chain import HITL_GATE_STEP
from academy_core.ledger import Ledger
from academy_core.models import (
    ROLE_CANONICAL_STEP,
    ChainContext,
    ChainRequest,
    HitlMode,
    Role,
    Scenario,
    StageResult,
)

#: Below this DECIDE confidence, an ESCALATION-mode gate routes to a human.
ESCALATION_THRESHOLD = 0.70

Approver = Callable[[str], bool]  # shown the proposal, returns approve/reject
Acknowledger = Callable[[str], bool]  # shown the proposal, returns acknowledged


@dataclass
class GateOutcome:
    """What happened at the step-16 gate."""

    mode: HitlMode
    approved: bool
    escalated: bool = False
    actor: str = "system"
    note: str = ""


@dataclass
class RunReport:
    """Everything one chain run produced — the object the CLI and tests inspect."""

    scenario: Scenario
    request: ChainRequest
    results: list[StageResult] = field(default_factory=list)
    gate: GateOutcome | None = None
    answer: str = ""
    escalation_route: str | None = None
    ledger: Ledger = field(default_factory=Ledger)

    @property
    def kpis(self) -> tuple[Any, ...]:
        return self.scenario.spec.kpis


class ChainRunner:
    """Runs scenarios against a ServiceHub, enforcing the HITL contract."""

    def __init__(
        self,
        services: Any,
        approver: Approver | None = None,
        acknowledger: Acknowledger | None = None,
    ) -> None:
        self.services = services
        self.approver = approver
        self.acknowledger = acknowledger

    def run(self, scenario: Scenario, request: ChainRequest | None = None) -> RunReport:
        spec = scenario.spec
        req = request or ChainRequest(spec.sample_employee, spec.sample_text)
        ctx = ChainContext(request=req, services=self.services)
        ctx.employee = self.services.employees.get(req.employee_id)
        report = RunReport(scenario=scenario, request=req)
        ledger = report.ledger
        persona = ctx.employee.get("name", req.employee_id)

        def log(step: int, stage: str, action: str, detail: str, **kw: Any) -> None:
            ledger.append(
                scenario_id=spec.scenario_id, step=step, stage=stage,
                agent=spec.lead_agent, persona=persona, action=action,
                detail=detail, hitl_mode=spec.hitl_mode.value, **kw,
            )

        # Step 11 — event trigger: the persona asked, or an event fired.
        log(11, "trigger", "scenario start", f"{persona!s}: {req.text!r} (locale {req.locale})")
        # Step 12 — the parent orchestrator dispatches the lead agent (MAF pattern: Sequential).
        log(12, "orchestrate", "agent dispatch",
            f"{spec.maf_pattern} pattern → lead agent {spec.lead_agent}")

        # Steps 13-16 — the decision plane.
        for role in (Role.ASSESS, Role.CLASSIFY, Role.QUANTIFY, Role.DECIDE):
            result = self._run_stage(scenario, role, ctx)
            if result is None:
                continue
            report.results.append(result)
            log(ROLE_CANONICAL_STEP[role], role.value, f"{role.value} complete",
                result.summary, confidence=result.confidence)

        # Step 16 — the one enforceable HITL gate.
        gate = self._gate(scenario, ctx)
        report.gate = gate
        log(
            HITL_GATE_STEP, "hitl-gate", f"{gate.mode.value} gate",
            gate.note, actor=gate.actor,
            outcome=(
                "escalated" if gate.escalated
                else "approved" if gate.approved
                else "pending"
            ),
        )

        # Step 17 — ACT runs only on an approved gate. Escalations route instead.
        if gate.approved:
            result = self._run_stage(scenario, Role.ACT, ctx)
            if result is not None:
                report.results.append(result)
                log(17, Role.ACT.value, "act + evidence-write", result.summary)
        else:
            route = ctx.state.get("route", "HR shared services (Sofia Ramos)")
            report.escalation_route = route if gate.escalated else None
            log(17, Role.ACT.value, "act skipped",
                f"routed to {route}" if gate.escalated else "awaiting human approval",
                outcome="escalated" if gate.escalated else "skipped")

        # Step 23 — LEARN closes the loop regardless of the gate outcome.
        result = self._run_stage(scenario, Role.LEARN, ctx)
        if result is not None:
            report.results.append(result)
            log(23, Role.LEARN.value, "feedback captured", result.summary)

        # Step 18 — KPI rollup: name the needles this run moves.
        kpi_names = ", ".join(k.name for k in spec.kpis)
        log(18, "kpi-rollup", "KPI attribution", f"moves: {kpi_names}")

        report.answer = self._answer(ctx, gate)
        return report

    def _run_stage(self, scenario: Scenario, role: Role, ctx: ChainContext) -> StageResult | None:
        handler = scenario.handlers.get(role)
        if handler is None:
            return None
        result = handler(ctx)
        ctx.results[role] = result
        return result

    def _gate(self, scenario: Scenario, ctx: ChainContext) -> GateOutcome:
        mode = scenario.spec.hitl_mode
        decide = ctx.results.get(Role.DECIDE)
        proposal = decide.summary if decide else "(no proposal)"
        confidence = decide.confidence if decide and decide.confidence is not None else 1.0

        if mode is HitlMode.ZERO_TOUCH:
            return GateOutcome(mode, approved=True,
                               note="touch-free: standard case, fully evidenced in the ledger")
        if mode is HitlMode.ACK_ONLY:
            ack_by = ctx.state.get("ack_by", "requesting persona")
            acked = self.acknowledger(proposal) if self.acknowledger else True
            return GateOutcome(mode, approved=acked, actor=ack_by,
                               note=f"acknowledged by {ack_by}" if acked else "not acknowledged")
        if mode is HitlMode.ESCALATION:
            if confidence >= ESCALATION_THRESHOLD:
                return GateOutcome(
                    mode, approved=True,
                    note=f"confidence {confidence:.2f} ≥ {ESCALATION_THRESHOLD} — auto-approved",
                )
            route = ctx.state.get("route", "HR shared services (Sofia Ramos)")
            return GateOutcome(
                mode, approved=False, escalated=True, actor=route,
                note=f"confidence {confidence:.2f} < {ESCALATION_THRESHOLD} — "
                     f"escalated to {route} with full context attached",
            )
        # HitlMode.HITL — hard gate: no approver callback means the chain waits.
        if self.approver is not None and self.approver(proposal):
            return GateOutcome(mode, approved=True, actor="human approver",
                               note="approved at the Adaptive Card gate")
        return GateOutcome(mode, approved=False, actor="human approver",
                           note="pending human approval — ACT withheld")

    @staticmethod
    def _answer(ctx: ChainContext, gate: GateOutcome) -> str:
        answer = ctx.state.get("answer", "")
        if not answer:
            decide = ctx.results.get(Role.DECIDE)
            answer = decide.summary if decide else ""
        if gate.escalated:
            route = ctx.state.get("route", "HR shared services")
            answer = (f"{answer}\n\n[escalated] A specialist ({route}) will follow up — "
                      "your full conversation and context travel with the case.")
        elif not gate.approved:
            answer = f"{answer}\n\n[pending] Awaiting human approval before any action is taken."
        return answer.strip()
