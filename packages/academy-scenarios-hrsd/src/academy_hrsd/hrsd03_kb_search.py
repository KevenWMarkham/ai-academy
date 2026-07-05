"""hr-hrsd-03 · HR knowledge-base search — finds the right policy & document.

Not question-answering: ranked, cited retrieval when the employee wants the
source itself. The Classify role IS the product here.
Brief: scenarios/hr-service-delivery/hr-hrsd-03-kb-search.md
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
    scenario_id="hr-hrsd-03",
    name="HR knowledge-base search",
    tagline="Finds the right policy and document, ranked and cited.",
    service="HR-HRSD-01 · Policy Q&A Copilot",
    chain_focus="Classify",
    hitl_mode=HitlMode.ZERO_TOUCH,
    lead_agent="KB-Search",
    personas=("Raj Patel", "Sofia Ramos"),
    kpis=(
        Kpi("Search success rate", "Sofia Ramos (HR Ops)", "48%", "85%",
            "semantic retrieval over a governed KB"),
        Kpi("Ticket deflection rate", "Sofia Ramos (HR Ops)", "0%", "55%",
            "employees find sources themselves"),
    ),
    azure_services=("Azure AI Search (hybrid/semantic)", "Azure OpenAI embeddings"),
    data_tools=("policy KB", "MCP search tool"),
    sample_text="Is there a stipend for home office equipment when working remote?",
)


def assess(ctx: ChainContext) -> StageResult:
    return StageResult(
        Role.ASSESS,
        f"Search scoped to documents {ctx.employee['name']} may read "
        f"(jurisdiction {ctx.employee['jurisdiction']}).",
    )


def classify(ctx: ChainContext) -> StageResult:
    hits = ctx.services.search.query(ctx.request.text, top=3)
    ctx.state["hits"] = hits
    summary = (
        f"Ranked {len(hits)} document(s); top: '{hits[0].title}' (score {hits[0].score})."
        if hits else "No documents matched."
    )
    return StageResult(Role.CLASSIFY, summary, confidence=hits[0].score if hits else 0.0)


def decide(ctx: ChainContext) -> StageResult:
    hits = ctx.state.get("hits") or []
    if not hits:
        ctx.state["answer"] = ("No policy matched. I've logged the gap — "
                               "HR shared services can help directly.")
        return StageResult(Role.DECIDE, "Zero-hit search — gap logged.", confidence=0.0)
    lines = [
        f"{i}. **{h.title}** ({h.doc_id}, score {h.score})\n   › {h.snippet[:160]}…"
        for i, h in enumerate(hits, 1)
    ]
    ctx.state["answer"] = "Here's what matched, best first:\n\n" + "\n".join(lines)
    return StageResult(Role.DECIDE, "Returned a ranked, cited result list.",
                       confidence=hits[0].score)


def act(ctx: ChainContext) -> StageResult:
    return StageResult(Role.ACT, "Result list delivered in Teams with open-document links.")


def learn(ctx: ChainContext) -> StageResult:
    hits = ctx.state.get("hits") or []
    note = "zero-hit query logged as a KB gap" if not hits else "query→click signal recorded"
    return StageResult(Role.LEARN, f"Search telemetry captured; {note}.")


SCENARIO = register(Scenario(SPEC, {
    Role.ASSESS: assess, Role.CLASSIFY: classify,
    Role.DECIDE: decide, Role.ACT: act, Role.LEARN: learn,
}))
