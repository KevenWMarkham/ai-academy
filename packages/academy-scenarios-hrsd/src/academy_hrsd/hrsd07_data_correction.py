"""hr-hrsd-07 · Data-correction request intake — captures & routes corrections.

Bad worker data poisons every downstream chain. This scenario detects the PII
in the request, structures the correction, and routes it to the owning data
team — with an ACK_ONLY gate so the employee confirms what will change.
Brief: scenarios/hr-service-delivery/hr-hrsd-07-data-correction.md
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
    scenario_id="hr-hrsd-07",
    name="Data-correction request intake",
    tagline="Captures a structured correction and routes it to the owning data team.",
    service="HR-HRSD-03 · Letter & Doc Generation",
    chain_focus="Act",
    hitl_mode=HitlMode.ACK_ONLY,
    lead_agent="Data-Correction",
    personas=("Raj Patel", "Sofia Ramos"),
    kpis=(
        Kpi("Intake SLA adherence", "Sofia Ramos (HR Ops)", "71%", "98%",
            "structured intake, no back-and-forth"),
        Kpi("Intake consistency", "Sofia Ramos (HR Ops)", "low", "100% structured",
            "every correction arrives complete"),
    ),
    azure_services=("Azure AI Language (PII/NER)", "Azure OpenAI (Foundry)"),
    data_tools=("gold_hr_case_v1", "ServiceNow HRSD", "MCP intake tool"),
    sample_text="My address is wrong — it should be 2189 Alameda Ave, San Jose CA 95126.",
)

FIELD_KEYWORDS: dict[str, tuple[str, ...]] = {
    "address": ("address", "moved", "live at", "residence"),
    "name": ("name is wrong", "name change", "misspelled"),
    "bank_details": ("bank", "account number", "direct deposit"),
    "emergency_contact": ("emergency contact",),
}


def assess(ctx: ChainContext) -> StageResult:
    return StageResult(
        Role.ASSESS,
        f"Read {ctx.employee['name']}'s current record values for comparison, scoped.",
    )


def classify(ctx: ChainContext) -> StageResult:
    intent = ctx.services.language.classify_intent(ctx.request.text, FIELD_KEYWORDS)
    pii = ctx.services.language.detect_pii(ctx.request.text)
    ctx.state["field"] = intent.intent
    ctx.state["pii"] = pii
    proposed = next((e.text for e in pii if e.category == "street_address"), None)
    ctx.state["proposed_value"] = proposed or "(provided in conversation)"
    return StageResult(
        Role.CLASSIFY,
        f"Correction target: '{intent.intent}'; {len(pii)} PII entit(ies) detected and "
        "handled per the tokenizer plane.",
        confidence=intent.confidence,
    )


def quantify(ctx: ChainContext) -> StageResult:
    field = ctx.state["field"]
    current = ctx.employee.get(field, "(not on record)")
    ctx.state["current_value"] = current
    return StageResult(
        Role.QUANTIFY,
        f"Structured the change: {field} — current {current!r} → proposed "
        f"{ctx.state['proposed_value']!r}.",
    )


def decide(ctx: ChainContext) -> StageResult:
    team = ctx.services.routing.route_for(ctx.request.text)
    ctx.state["team"] = team
    ctx.state["ack_by"] = f"{ctx.employee['name']} (requesting employee)"
    ctx.state["answer"] = (
        f"I'll submit this correction for you:\n\n"
        f"- Field: **{ctx.state['field']}**\n"
        f"- Current: {ctx.state['current_value']}\n"
        f"- Proposed: {ctx.state['proposed_value']}\n"
        f"- Routed to: {team['team']} (SLA {team['sla_days']} days)\n\n"
        "Please confirm and I'll file it."
    )
    return StageResult(
        Role.DECIDE,
        f"Correction structured and routed to {team['team']}, pending acknowledgment.",
        confidence=max(ctx.results[Role.CLASSIFY].confidence, 0.75),
    )


def act(ctx: ChainContext) -> StageResult:
    team = ctx.state["team"]
    case = ctx.services.cases.open_case({
        "employee_id": ctx.request.employee_id,
        "type": f"Data correction: {ctx.state['field']}",
        "stage": "With data team",
        "owner": team["owner"],
    })
    return StageResult(
        Role.ACT,
        f"Correction case {case['case_id']} filed with {team['team']}; "
        "employee gets status updates via hr-hrsd-02.",
    )


def learn(ctx: ChainContext) -> StageResult:
    return StageResult(
        Role.LEARN,
        "Correction frequency by field feeds data-quality dashboards — chronic offenders "
        "get fixed at the source system.",
    )


SCENARIO = register(Scenario(SPEC, {
    Role.ASSESS: assess, Role.CLASSIFY: classify, Role.QUANTIFY: quantify,
    Role.DECIDE: decide, Role.ACT: act, Role.LEARN: learn,
}))
