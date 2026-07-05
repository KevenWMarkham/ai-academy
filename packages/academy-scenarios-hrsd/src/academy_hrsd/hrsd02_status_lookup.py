"""hr-hrsd-02 · Status lookup — "where's my request?", answered instantly.

A top ticket driver. Status-Lookup reads cases, requests and approvals —
scoped strictly to what the employee is allowed to see. A pure read: the
cheapest possible ZERO_TOUCH chain.
Brief: scenarios/hr-service-delivery/hr-hrsd-02-status-lookup.md
"""

from __future__ import annotations

from academy_core.models import (
    ChainContext,
    HitlMode,
    Kpi,
    Role,
    Scenario,
    ScenarioSpec,
    StageResult,
)
from academy_core.registry import register

#: A case sitting in one stage longer than this is "stuck" and pinged to its owner.
STUCK_AFTER_DAYS = 7

SPEC = ScenarioSpec(
    scenario_id="hr-hrsd-02",
    name="Status lookup",
    tagline='"Where\'s my request?" answered instantly, scoped to the asker.',
    service="HR-HRSD-01 · Policy Q&A Copilot",
    chain_focus="Assess",
    hitl_mode=HitlMode.ZERO_TOUCH,
    lead_agent="Status-Lookup",
    personas=("Raj Patel",),
    kpis=(
        Kpi("Status-ticket volume", "Sofia Ramos (HR Ops)", "high", "-70%",
            "self-service status reads"),
        Kpi("Average handle time", "Raj Patel (Employee)", "2 days", "2 min",
            "instant answers & docs"),
    ),
    azure_services=("Azure OpenAI (Foundry)", "Microsoft Agent Framework"),
    data_tools=("ServiceNow HRSD", "gold_hr_case_v1", "MCP status tool"),
    sample_text="Where is my tuition reimbursement request?",
)


def assess(ctx: ChainContext) -> StageResult:
    cases = ctx.services.cases.for_employee(ctx.request.employee_id)
    ctx.state["cases"] = cases
    return StageResult(
        Role.ASSESS,
        f"Read {len(cases)} case(s) visible to {ctx.employee['name']} — scoped to them only.",
    )


def classify(ctx: ChainContext) -> StageResult:
    lowered = ctx.request.text.lower()
    cases = ctx.state["cases"]
    match = next(
        (c for c in cases if any(w in lowered for w in c["type"].lower().split())),
        None,
    ) or (cases[0] if len(cases) == 1 else None)
    ctx.state["case"] = match
    if match is None:
        return StageResult(Role.CLASSIFY, "Could not identify which request was meant.",
                           confidence=0.3)
    return StageResult(Role.CLASSIFY,
                       f"Identified {match['case_id']} ({match['type']}), "
                       f"currently at stage '{match['stage']}'.", confidence=0.9)


def decide(ctx: ChainContext) -> StageResult:
    case = ctx.state.get("case")
    if case is None:
        opts = ", ".join(f"{c['case_id']} ({c['type']})" for c in ctx.state["cases"])
        ctx.state["answer"] = f"I found several requests — which did you mean? {opts}"
        return StageResult(Role.DECIDE, "Asked the employee to disambiguate.", confidence=0.5)
    ctx.state["answer"] = ctx.services.chat.polish(
        f"Your **{case['type']}** request ({case['case_id']}) is at stage "
        f"**{case['stage']}** with {case['owner']}, expected to complete by "
        f"{case['expected']}.", persona=ctx.employee["name"],
    )
    return StageResult(Role.DECIDE, f"Status, owner and expected date for {case['case_id']}.",
                       confidence=0.95)


def act(ctx: ChainContext) -> StageResult:
    return StageResult(Role.ACT, "Pure read delivered in Teams — no human needed, no mutation.")


def learn(ctx: ChainContext) -> StageResult:
    case = ctx.state.get("case")
    if case and case.get("days_in_stage", 0) > STUCK_AFTER_DAYS:
        return StageResult(
            Role.LEARN,
            f"{case['case_id']} has sat {case['days_in_stage']}d in one stage — "
            f"owner {case['owner']} pinged; lookup pattern logged as a process bottleneck.",
        )
    return StageResult(Role.LEARN, "Lookup pattern recorded for bottleneck analytics.")


SCENARIO = register(Scenario(SPEC, {
    Role.ASSESS: assess, Role.CLASSIFY: classify,
    Role.DECIDE: decide, Role.ACT: act, Role.LEARN: learn,
}))
