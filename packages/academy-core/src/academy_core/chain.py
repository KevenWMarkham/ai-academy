"""The canonical 24-step chain — the enterprise backbone every scenario specializes.

Three waves: W1 foundation (steps 1-10) builds the planes once per enterprise;
W2 pilot (11-18) is the segment the academy scenarios execute; W3 scale & fuse
(19-24) is where chains multiply and compound. Scenarios specialize titles and
purposes but keep 1..24 and exactly one HITL gate at step 16.

Source of truth: the production ``scenario_chain`` platform's taxonomy.
"""

from __future__ import annotations

from typing import TypedDict


class CanonicalStep(TypedDict):
    step: int
    wave: str
    key: str
    title: str
    layer: str
    kind: str


CANONICAL_24_STEP_CHAIN: tuple[CanonicalStep, ...] = (
    {"step": 1, "wave": "W1", "key": "w1-sor", "title": "SOR · System of Record",
     "layer": "Integration Plane · SOR", "kind": "source"},
    {"step": 2, "wave": "W1", "key": "w1-rth", "title": "Real-Time Hub · streaming ingest",
     "layer": "Integration Plane", "kind": "ingest"},
    {"step": 3, "wave": "W1", "key": "w1-bronze", "title": "Bronze landing · raw + ingest metadata",
     "layer": "Data Plane · Bronze", "kind": "data"},
    {"step": 4, "wave": "W1", "key": "w1-tokenizer", "title": "Tokenizer / PII handling",
     "layer": "Data Plane · Bronze", "kind": "transform"},
    {"step": 5, "wave": "W1", "key": "w1-silver",
     "title": "Silver canonical · MERML / SCML / FINML",
     "layer": "Data Plane · Silver", "kind": "canonical"},
    {"step": 6, "wave": "W1", "key": "w1-gold", "title": "Gold semantic · Power BI Direct Lake",
     "layer": "Data Plane · Gold", "kind": "semantic"},
    {"step": 7, "wave": "W1", "key": "w1-mcp", "title": "MCP server · capability registry",
     "layer": "Runtime Plane", "kind": "runtime"},
    {"step": 8, "wave": "W1", "key": "w1-identity", "title": "Entra · agent + persona identities",
     "layer": "Identity Plane", "kind": "identity"},
    {"step": 9, "wave": "W1", "key": "w1-ledger", "title": "LEDGER · 14-field audit row store",
     "layer": "Ledger Plane", "kind": "evidence"},
    {"step": 10, "wave": "W1", "key": "w1-hitl-surface", "title": "HITL Adaptive Card surface",
     "layer": "Experience Plane", "kind": "hitl"},
    {"step": 11, "wave": "W2", "key": "w2-event", "title": "Event trigger · scenario start",
     "layer": "Runtime Plane", "kind": "trigger"},
    {"step": 12, "wave": "W2", "key": "w2-orchestrator",
     "title": "Parent orchestrator · agent dispatch",
     "layer": "Runtime Plane · MAF", "kind": "orchestrate"},
    {"step": 13, "wave": "W2", "key": "w2-agent-assess", "title": "Assess / Sense agent",
     "layer": "Decision Plane", "kind": "agent"},
    {"step": 14, "wave": "W2", "key": "w2-agent-classify", "title": "Classify / Score agent",
     "layer": "Decision Plane", "kind": "agent"},
    {"step": 15, "wave": "W2", "key": "w2-agent-quantify", "title": "Quantify / Compose agent",
     "layer": "Decision Plane", "kind": "agent"},
    {"step": 16, "wave": "W2", "key": "w2-hitl", "title": "HITL gate · Adaptive Card",
     "layer": "Experience Plane · HITL", "kind": "hitl"},
    {"step": 17, "wave": "W2", "key": "w2-agent-act", "title": "Act + Evidence-Write",
     "layer": "Decision Plane · Mutation", "kind": "agent"},
    {"step": 18, "wave": "W2", "key": "w2-kpi", "title": "KPI rollup · Power BI semantic model",
     "layer": "Experience Plane · BI", "kind": "kpi"},
    {"step": 19, "wave": "W3", "key": "w3-scale", "title": "Scale · multi-tenant · multi-banner",
     "layer": "Runtime · Scale", "kind": "scale"},
    {"step": 20, "wave": "W3", "key": "w3-fuse-adjacent", "title": "Fuse · adjacent scenarios",
     "layer": "Runtime · Fusion", "kind": "fuse"},
    {"step": 21, "wave": "W3", "key": "w3-fuse-cross", "title": "Fuse · cross-Practice",
     "layer": "Runtime · Fusion", "kind": "fuse"},
    {"step": 22, "wave": "W3", "key": "w3-purview",
     "title": "Purview · lineage + classification at scale",
     "layer": "Governance Plane", "kind": "governance"},
    {"step": 23, "wave": "W3", "key": "w3-ledger-feedback",
     "title": "LEDGER feedback loop · model retraining",
     "layer": "Ledger · Feedback", "kind": "feedback"},
    {"step": 24, "wave": "W3", "key": "w3-kpi-enterprise",
     "title": "Enterprise KPI · run-rate durable value",
     "layer": "Experience · Executive", "kind": "kpi"},
)

#: The single enforceable HITL gate in the canonical chain.
HITL_GATE_STEP = 16

#: The steps the academy runtime actually executes (the W2 pilot segment + the learn loop).
EXECUTED_STEPS = (11, 12, 13, 14, 15, 16, 17, 18, 23)


def wave_for_step(step: int) -> str:
    """Return the wave (``W1``/``W2``/``W3``) for a 1..24 step number."""
    if 1 <= step <= 10:
        return "W1"
    if 11 <= step <= 18:
        return "W2"
    return "W3"
