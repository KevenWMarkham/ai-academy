"""hr-hrsd-06 · Letter & document generation — self-served, jurisdiction-correct.

High volume, fully templated, yet still manual in most HR shops. Doc-Gen
validates the data, renders the letter, and asks only for an acknowledgment
(ACK_ONLY) before generating and logging it.
Brief: scenarios/hr-service-delivery/hr-hrsd-06-doc-generation.md
"""

from __future__ import annotations

from datetime import date

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
    scenario_id="hr-hrsd-06",
    name="Letter & document generation",
    tagline="Employment letters on demand — personalized, jurisdiction-correct, logged.",
    service="HR-HRSD-03 · Letter & Doc Generation",
    chain_focus="Act",
    hitl_mode=HitlMode.ACK_ONLY,
    lead_agent="Doc-Gen",
    personas=("Raj Patel", "Sofia Ramos"),
    kpis=(
        Kpi("Document turnaround", "Sofia Ramos (HR Ops)", "3 days", "instant",
            "templated self-service generation"),
        Kpi("Self-serve rate", "Sofia Ramos (HR Ops)", "5%", "80%",
            "employees generate their own letters"),
    ),
    azure_services=("Azure OpenAI (Foundry)", "Azure AI Document Intelligence",
                    "Microsoft Purview (audit)"),
    data_tools=("gold_hr_worker_v2", "MCP doc-gen tool", "Purview audit"),
    sample_text="I need an employment verification letter for my mortgage application.",
)

TEMPLATE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "employment-verification": ("verification", "verify", "employment letter", "mortgage",
                                "landlord", "visa"),
    "leave-confirmation": ("leave confirmation", "confirm my leave", "leave letter"),
}


def assess(ctx: ChainContext) -> StageResult:
    return StageResult(
        Role.ASSESS,
        f"Read the data required for the letter from {ctx.employee['name']}'s worker record, "
        "scoped to the fields the template needs.",
    )


def classify(ctx: ChainContext) -> StageResult:
    intent = ctx.services.language.classify_intent(ctx.request.text, TEMPLATE_KEYWORDS)
    template = intent.intent if intent.intent != "unknown" else "employment-verification"
    ctx.state["template"] = template
    return StageResult(
        Role.CLASSIFY,
        f"Selected template '{template}' with {ctx.employee['jurisdiction']} "
        "jurisdiction language.",
        confidence=max(intent.confidence, 0.6),
    )


def quantify(ctx: ChainContext) -> StageResult:
    fields = {**ctx.employee, "issue_date": date.today().isoformat()}
    ctx.state["fields"] = fields
    required = ctx.services.documents.required_fields(ctx.state["template"])
    missing = [f for f in required if not fields.get(f)]
    ctx.state["missing"] = missing
    detail = f"missing: {', '.join(missing)}" if missing else "all fields present and current"
    return StageResult(Role.QUANTIFY, f"Validated {len(required)} required field(s) — {detail}.")


def decide(ctx: ChainContext) -> StageResult:
    if ctx.state["missing"]:
        ctx.state["answer"] = (
            "I can't generate the letter yet — your record is missing: "
            + ", ".join(ctx.state["missing"]) + ". A data-correction request will fix that first."
        )
        return StageResult(Role.DECIDE, "Blocked on incomplete data.", confidence=0.4)
    doc = ctx.services.documents.render(ctx.state["template"], ctx.state["fields"])
    ctx.state["document"] = doc
    ctx.state["ack_by"] = f"{ctx.employee['name']} (requesting employee)"
    ctx.state["answer"] = f"Here is your **{doc.title}** — please review:\n\n---\n{doc.body}"
    return StageResult(Role.DECIDE, f"Drafted '{doc.title}' from template '{doc.template}'.",
                       confidence=0.95)


def act(ctx: ChainContext) -> StageResult:
    doc = ctx.state.get("document")
    if doc is None:
        return StageResult(Role.ACT, "Nothing generated — data was incomplete.")
    return StageResult(
        Role.ACT,
        f"'{doc.title}' generated as PDF, delivered in Teams, and logged to the "
        "Purview audit trail.",
    )


def learn(ctx: ChainContext) -> StageResult:
    return StageResult(
        Role.LEARN,
        "Request volume by letter type informs which documents to add to self-service next.",
    )


SCENARIO = register(Scenario(SPEC, {
    Role.ASSESS: assess, Role.CLASSIFY: classify, Role.QUANTIFY: quantify,
    Role.DECIDE: decide, Role.ACT: act, Role.LEARN: learn,
}))
