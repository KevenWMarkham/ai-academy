"""hr-hrsd-05 · Leave & absence guidance — options, dates and steps.

Leave is where policy complexity meets personal anxiety. The chain grounds on
the right leave policy, quantifies the employee's actual balances and
jurisdiction benefits, and lays out a concrete plan.
Brief: scenarios/hr-service-delivery/hr-hrsd-05-leave-absence.md
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

SPEC = ScenarioSpec(
    scenario_id="hr-hrsd-05",
    name="Leave & absence guidance",
    tagline="Options, dates and steps for any leave — grounded on policy and balances.",
    service="HR-HRSD-02 · Life-Event Navigator",
    chain_focus="Classify → Decide",
    hitl_mode=HitlMode.ZERO_TOUCH,
    lead_agent="Leave-Guide",
    personas=("Raj Patel", "Sofia Ramos"),
    kpis=(
        Kpi("Leave-question deflection", "Sofia Ramos (HR Ops)", "0%", "60%",
            "grounded guidance instead of tickets"),
        Kpi("Employee CSAT", "Sofia Ramos (HR Ops)", "3.6", "4.5 / 5",
            "clear options at a stressful moment"),
    ),
    azure_services=("Azure AI Language (CLU intent)", "Azure AI Search",
                    "Azure OpenAI (Foundry)"),
    data_tools=("gold_hr_worker_v2", "leave policy KB", "MCP leave tool"),
    sample_text="I need to take time off to care for my father after surgery.",
)

INTENTS: dict[str, tuple[str, ...]] = {
    "caregiver": ("care for", "caring for", "father", "mother", "spouse", "surgery", "ill"),
    "parental": ("baby", "birth", "adopt", "parental", "maternity", "paternity"),
    "medical": ("my surgery", "hospitalized", "medical leave", "disability"),
    "bereavement": ("passed away", "funeral", "bereavement"),
    "vacation": ("vacation", "holiday", "pto", "trip"),
}

POLICY_QUERY: dict[str, str] = {
    "caregiver": "caregiver leave family serious health condition",
    "parental": "parental leave primary secondary caregiver weeks",
    "medical": "medical leave short-term disability weeks",
    "bereavement": "bereavement leave paid days immediate family",
    "vacation": "PTO accrual carry over vacation days",
}


def assess(ctx: ChainContext) -> StageResult:
    emp = ctx.employee
    return StageResult(
        Role.ASSESS,
        f"Read {emp['name']}'s balances (PTO {emp['pto_balance_days']}d, "
        f"sick {emp['sick_balance_days']}d) and jurisdiction {emp['jurisdiction']}.",
    )


def classify(ctx: ChainContext) -> StageResult:
    intent = ctx.services.language.classify_intent(ctx.request.text, INTENTS)
    ctx.state["leave_type"] = intent.intent
    hits = ctx.services.search.query(POLICY_QUERY.get(intent.intent, ctx.request.text))
    ctx.state["hits"] = hits
    grounded = f"; grounded on '{hits[0].title}'" if hits else ""
    return StageResult(
        Role.CLASSIFY,
        f"Leave type: {intent.intent} (evidence: {', '.join(intent.evidence) or '—'}){grounded}.",
        confidence=intent.confidence,
    )


def quantify(ctx: ChainContext) -> StageResult:
    emp = ctx.employee
    options: list[str] = []
    if ctx.state["leave_type"] == "caregiver":
        options.append("Up to 12 weeks job-protected caregiver leave "
                       "(first 2 weeks paid — POL-LVE-032)")
        if emp["jurisdiction"] == "US-CA":
            options.append("CA Paid Family Leave: up to 8 weeks partial wage replacement, "
                           "concurrent")
    if emp["sick_balance_days"]:
        options.append(f"{emp['sick_balance_days']} sick days can cover unpaid periods first")
    if emp["pto_balance_days"]:
        options.append(f"{emp['pto_balance_days']} PTO days can be applied after sick balance")
    ctx.state["options"] = options
    return StageResult(Role.QUANTIFY,
                       f"Quantified {len(options)} option(s) from balances and jurisdiction.")


def decide(ctx: ChainContext) -> StageResult:
    hits = ctx.state.get("hits") or []
    cite = f" [source: {hits[0].doc_id}]" if hits else ""
    option_lines = "\n".join(f"- {o}" for o in ctx.state.get("options", []))
    ctx.state["answer"] = ctx.services.chat.polish(
        f"I'm sorry about your father — here are your options:{cite}\n\n{option_lines}\n\n"
        "Next steps: tell your manager, open a leave case (I can do that now), and provide "
        "the care certification within 15 days.",
        persona=ctx.employee["name"],
    )
    return StageResult(Role.DECIDE, "Laid out leave options, pay treatment and next steps.",
                       confidence=ctx.results[Role.CLASSIFY].confidence)


def act(ctx: ChainContext) -> StageResult:
    case = ctx.services.cases.open_case({
        "employee_id": ctx.request.employee_id,
        "type": f"Leave guidance: {ctx.state['leave_type']}",
        "stage": "Awaiting employee confirmation",
        "owner": "Leave-Guide",
    })
    return StageResult(Role.ACT, f"Draft leave case {case['case_id']} opened, touch-free.")


def learn(ctx: ChainContext) -> StageResult:
    return StageResult(Role.LEARN,
                       "Guidance-to-leave conversion tracked; unclear policies flagged to HR Ops.")


SCENARIO = register(Scenario(SPEC, {
    Role.ASSESS: assess, Role.CLASSIFY: classify, Role.QUANTIFY: quantify,
    Role.DECIDE: decide, Role.ACT: act, Role.LEARN: learn,
}))
