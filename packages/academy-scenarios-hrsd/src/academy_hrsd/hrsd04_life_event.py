"""hr-hrsd-04 · Life-event guidance — guided through change, in order, on time.

A new baby, a move, a bereavement: each triggers a web of HR actions employees
don't know how to navigate. The Navigator identifies everything the event
triggers and sequences it by deadline.
Brief: scenarios/hr-service-delivery/hr-hrsd-04-life-event.md
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
    scenario_id="hr-hrsd-04",
    name="Life-event guidance",
    tagline="Walks employees through every step a life event triggers — personalized, in order.",
    service="HR-HRSD-02 · Life-Event Navigator",
    chain_focus="Classify → Decide",
    hitl_mode=HitlMode.ZERO_TOUCH,
    lead_agent="Life-Event-Navigator",
    personas=("Raj Patel", "Sofia Ramos"),
    kpis=(
        Kpi("Life-event completion rate", "Sofia Ramos (HR Ops)", "62%", "95%",
            "sequenced, deadline-aware guidance"),
        Kpi("Employee CSAT", "Sofia Ramos (HR Ops)", "3.6", "4.5 / 5",
            "fast, accurate, 24×7"),
    ),
    azure_services=("Azure AI Language (CLU intent)", "Azure OpenAI (Foundry)",
                    "Microsoft Agent Framework"),
    data_tools=("gold_hr_worker_v2", "benefits/policy KB", "MCP life-event tool"),
    sample_text="We just had a baby! What do I need to do?",
)

INTENTS: dict[str, tuple[str, ...]] = {
    "new_child": ("baby", "birth", "born", "adopt", "newborn", "child arrived"),
    "move": ("moved", "moving", "relocat", "new apartment", "new house"),
    "bereavement": ("passed away", "death in", "funeral", "lost my"),
    "marriage": ("married", "marriage", "wedding"),
}

#: What each event triggers, sequenced by deadline (days from the event).
CHECKLISTS: dict[str, tuple[tuple[int, str], ...]] = {
    "new_child": (
        (30, "Elect parental leave dates (16w primary / 6w secondary — POL-LVE-031)"),
        (31, "Add the dependent to medical/dental (special enrollment window)"),
        (45, "Update tax withholding and beneficiaries if desired"),
        (60, "Review EAP new-parent resources"),
    ),
    "move": (
        (30, "Update your address in the worker record (POL-WRK-007)"),
        (30, "Confirm the new location is a compliant work location"),
        (45, "Re-check state/country tax withholding"),
    ),
    "bereavement": (
        (0, "Take bereavement leave — up to 10 paid days for immediate family (POL-LVE-033)"),
        (30, "Update beneficiaries and dependents if affected"),
        (60, "EAP grief counselling — 6 confidential sessions, free"),
    ),
    "marriage": (
        (31, "Add your spouse to benefits (special enrollment window)"),
        (45, "Update name/records if changing (HR Data Services)"),
        (45, "Review beneficiaries and tax withholding"),
    ),
}


def assess(ctx: ChainContext) -> StageResult:
    emp = ctx.employee
    return StageResult(
        Role.ASSESS,
        f"Read {emp['name']}'s situation and eligibility "
        f"(jurisdiction {emp['jurisdiction']}, {emp['dependents']} dependent(s) on file).",
    )


def classify(ctx: ChainContext) -> StageResult:
    intent = ctx.services.language.classify_intent(ctx.request.text, INTENTS)
    ctx.state["event"] = intent.intent
    return StageResult(
        Role.CLASSIFY,
        f"Life event identified: {intent.intent} (evidence: {', '.join(intent.evidence) or '—'}).",
        confidence=intent.confidence,
    )


def quantify(ctx: ChainContext) -> StageResult:
    event = ctx.state["event"]
    checklist = CHECKLISTS.get(event, ())
    ctx.state["checklist"] = checklist
    return StageResult(
        Role.QUANTIFY,
        f"{len(checklist)} triggered action(s) sequenced by deadline for event '{event}'.",
    )


def decide(ctx: ChainContext) -> StageResult:
    event = ctx.state["event"]
    checklist = ctx.state.get("checklist") or ()
    if event == "unknown" or not checklist:
        ctx.state["answer"] = ("I couldn't map that to a known life event — "
                               "routing you to HR shared services.")
        ctx.state["route"] = "HR shared services (Sofia Ramos)"
        return StageResult(Role.DECIDE, "Unrecognized life event.", confidence=0.2)
    steps = "\n".join(
        f"{i}. (within {days} days) {action}" for i, (days, action) in enumerate(checklist, 1)
    )
    congrats = "Congratulations! " if event in ("new_child", "marriage") else ""
    ctx.state["answer"] = ctx.services.chat.polish(
        f"{congrats}Here is your personalized plan, in deadline order:\n\n{steps}\n\n"
        "I can kick off each task for you — say the word.",
        persona=ctx.employee["name"],
    )
    return StageResult(Role.DECIDE, f"Laid out options, dates and next steps for '{event}'.",
                       confidence=ctx.results[Role.CLASSIFY].confidence)


def act(ctx: ChainContext) -> StageResult:
    event = ctx.state["event"]
    case = ctx.services.cases.open_case({
        "employee_id": ctx.request.employee_id,
        "type": f"Life event: {event}",
        "stage": "Guidance delivered",
        "owner": "Life-Event-Navigator",
    })
    return StageResult(Role.ACT, f"Guidance delivered; tracking case {case['case_id']} opened.")


def learn(ctx: ChainContext) -> StageResult:
    return StageResult(
        Role.LEARN,
        "Completion of each checklist step is tracked; drop-offs refine the flow, "
        "edge cases route to Sofia.",
    )


SCENARIO = register(Scenario(SPEC, {
    Role.ASSESS: assess, Role.CLASSIFY: classify, Role.QUANTIFY: quantify,
    Role.DECIDE: decide, Role.ACT: act, Role.LEARN: learn,
}))
