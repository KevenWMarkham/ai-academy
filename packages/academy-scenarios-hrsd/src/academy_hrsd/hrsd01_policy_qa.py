"""hr-hrsd-01 · Policy Q&A — instant, grounded answers before a ticket is raised.

Most HR tickets are policy questions with a known answer. Policy-QA answers
them in Teams — grounded on the actual policy and the employee's own context.
Brief: scenarios/hr-service-delivery/hr-hrsd-01-policy-qa.md
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
    scenario_id="hr-hrsd-01",
    name="Policy Q&A",
    tagline="Instant, grounded policy answers in Teams — before a ticket is ever raised.",
    service="HR-HRSD-01 · Policy Q&A Copilot",
    chain_focus="Classify",
    hitl_mode=HitlMode.ZERO_TOUCH,
    lead_agent="Policy-QA",
    personas=("Raj Patel", "Sofia Ramos"),
    kpis=(
        Kpi("Ticket deflection rate", "Sofia Ramos (HR Ops)", "0%", "55%",
            "grounded self-service in Teams"),
        Kpi("First-contact resolution", "Sofia Ramos (HR Ops)", "61%", "89%",
            "single grounded agent"),
    ),
    azure_services=("Azure OpenAI (Foundry)", "Azure AI Search", "Microsoft Agent Framework"),
    data_tools=("gold_hr_worker_v2", "policy KB", "MCP policy-QA tool"),
    sample_text="How many unused PTO days can I carry over into next year?",
)


def assess(ctx: ChainContext) -> StageResult:
    emp = ctx.employee
    return StageResult(
        Role.ASSESS,
        f"Read {emp['name']}'s worker context, scoped to them only "
        f"(jurisdiction {emp['jurisdiction']}, tenure {emp['tenure_years']}y, "
        f"PTO balance {emp['pto_balance_days']}d).",
    )


def classify(ctx: ChainContext) -> StageResult:
    hits = ctx.services.search.query(ctx.request.text)
    ctx.state["hits"] = hits
    if not hits:
        return StageResult(Role.CLASSIFY, "No policy matched the question.", confidence=0.0)
    top = hits[0]
    return StageResult(
        Role.CLASSIFY,
        f"Grounded on '{top.title}' ({top.doc_id}, score {top.score}).",
        data={"doc_id": top.doc_id},
        confidence=top.score,
    )


def quantify(ctx: ChainContext) -> StageResult:
    hits = ctx.state.get("hits") or []
    emp = ctx.employee
    exceptions: list[str] = []
    if hits:
        body = open(hits[0].path, encoding="utf-8").read()  # noqa: SIM115
        if emp["jurisdiction"] in body:
            exceptions.append(f"a {emp['jurisdiction']} jurisdiction rider applies")
    if not exceptions:
        exceptions.append("no personal exceptions apply")
    ctx.state["exceptions"] = exceptions
    return StageResult(Role.QUANTIFY, f"Checked exceptions for {emp['name']}: "
                                      + "; ".join(exceptions) + ".")


def decide(ctx: ChainContext) -> StageResult:
    hits = ctx.state.get("hits") or []
    emp = ctx.employee
    if not hits:
        ctx.state["answer"] = (
            "I couldn't find a policy that answers that — routing you to HR shared services."
        )
        return StageResult(Role.DECIDE, "No grounded answer available.", confidence=0.0)
    top = hits[0]
    draft = (
        f"Per **{top.title}**: {top.snippet}\n\n"
        f"For you specifically ({emp['jurisdiction']}): {'; '.join(ctx.state['exceptions'])}. "
        f"Your current PTO balance is {emp['pto_balance_days']} days.\n"
        f"[source: {top.doc_id}]"
    )
    ctx.state["answer"] = ctx.services.chat.polish(draft, persona=emp["name"])
    return StageResult(Role.DECIDE, f"Composed a cited answer from {top.doc_id}.",
                       confidence=top.score)


def act(ctx: ChainContext) -> StageResult:
    return StageResult(Role.ACT, "Answer delivered in Teams; no ticket raised.")


def learn(ctx: ChainContext) -> StageResult:
    hits = ctx.state.get("hits") or []
    score = hits[0].score if hits else 0.0
    gap = "knowledge-base gap flagged for HR Ops" if score < 0.4 else "no KB gap"
    return StageResult(Role.LEARN, f"Answer quality recorded (grounding score {score}); {gap}.")


SCENARIO = register(Scenario(SPEC, {
    Role.ASSESS: assess, Role.CLASSIFY: classify, Role.QUANTIFY: quantify,
    Role.DECIDE: decide, Role.ACT: act, Role.LEARN: learn,
}))
