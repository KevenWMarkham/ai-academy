"""hr-hrsd-08 · Ticket deflection / smart routing — resolve or route precisely.

When the agent can't fully resolve, the worst outcome is a *misrouted* ticket.
Deflection resolves what it can; below the confidence threshold the ESCALATION
gate routes to the right team with the full context attached. This is the
scenario where students watch the step-16 gate actually fire.
Brief: scenarios/hr-service-delivery/hr-hrsd-08-deflection.md
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

#: KB grounding at or above this lets the agent resolve directly.
RESOLVE_THRESHOLD = 0.60

SPEC = ScenarioSpec(
    scenario_id="hr-hrsd-08",
    name="Ticket deflection / smart routing",
    tagline="Resolves what it can; routes the rest precisely, with full context attached.",
    service="HR-HRSD-04 · Ticket Deflection",
    chain_focus="Decide",
    hitl_mode=HitlMode.ESCALATION,
    lead_agent="Deflection",
    personas=("Sofia Ramos", "Raj Patel"),
    kpis=(
        Kpi("Ticket deflection rate", "Sofia Ramos (HR Ops)", "0%", "55%",
            "resolve-at-source before ticketing"),
        Kpi("Misroute rate", "Sofia Ramos (HR Ops)", "23%", "<3%",
            "confidence-scored routing with context"),
    ),
    azure_services=("Azure AI Language (classification)", "Azure OpenAI (Foundry)",
                    "Microsoft Agent Framework"),
    data_tools=("ServiceNow HRSD", "MCP routing tool"),
    sample_text=("My paycheck was garnished incorrectly after my divorce settlement — "
                 "who do I talk to?"),
)


def assess(ctx: ChainContext) -> StageResult:
    return StageResult(
        Role.ASSESS,
        f"Read the full conversation and {ctx.employee['name']}'s context on an "
        "unresolved query.",
    )


def classify(ctx: ChainContext) -> StageResult:
    hits = ctx.services.search.query(ctx.request.text)
    score = hits[0].score if hits else 0.0
    ctx.state["hits"], ctx.state["kb_score"] = hits, score
    resolvable = score >= RESOLVE_THRESHOLD
    ctx.state["resolvable"] = resolvable
    return StageResult(
        Role.CLASSIFY,
        f"KB grounding score {score:.2f} → "
        f"{'can resolve directly' if resolvable else 'must route'}.",
        confidence=score,
    )


def quantify(ctx: ChainContext) -> StageResult:
    team = ctx.services.routing.route_for(ctx.request.text)
    ctx.state["team"] = team
    ctx.state["route"] = f"{team['team']} ({team['owner']}, SLA {team['sla_days']}d)"
    return StageResult(
        Role.QUANTIFY,
        f"Confidence scored; best destination if routing: {team['team']}.",
        confidence=ctx.state["kb_score"],
    )


def decide(ctx: ChainContext) -> StageResult:
    if ctx.state["resolvable"]:
        top = ctx.state["hits"][0]
        ctx.state["answer"] = ctx.services.chat.polish(
            f"Per **{top.title}**: {top.snippet} [source: {top.doc_id}]",
            persona=ctx.employee["name"],
        )
        return StageResult(Role.DECIDE, f"Resolved directly from {top.doc_id}.",
                           confidence=max(ctx.state["kb_score"], 0.8))
    team = ctx.state["team"]
    ctx.state["answer"] = (
        f"This needs a specialist. I'm routing you to **{team['team']}** with your full "
        f"context attached — expect a response within {team['sla_days']} business days."
    )
    return StageResult(
        Role.DECIDE,
        f"Cannot resolve (KB score {ctx.state['kb_score']:.2f}); proposing route to "
        f"{team['team']} with a complete context package.",
        confidence=ctx.state["kb_score"],
    )


def act(ctx: ChainContext) -> StageResult:
    # Runs only when the gate auto-approved (high confidence): the direct resolution.
    return StageResult(Role.ACT, "Resolved at source — no ticket created.")


def learn(ctx: ChainContext) -> StageResult:
    return StageResult(
        Role.LEARN,
        "Resolve-vs-route outcome recorded; misroutes retrain the boundary so the "
        "threshold earns trust over time.",
    )


SCENARIO = register(Scenario(SPEC, {
    Role.ASSESS: assess, Role.CLASSIFY: classify, Role.QUANTIFY: quantify,
    Role.DECIDE: decide, Role.ACT: act, Role.LEARN: learn,
}))
