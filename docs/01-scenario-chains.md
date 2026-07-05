# 01 · Scenario Chains — the canonical 24-step chain

## The premise

An AI service that answers a question is a demo. A **scenario chain** is a production system:
agents in named roles, running on governed data, gated by a human where it matters, leaving
evidence at every step, and rolling up to a KPI a named business persona owns. The chain — not
the model — is the unit of enterprise value.

Every scenario in this academy specializes the same **canonical 24-step chain**. Scenarios
change titles and purposes, but they keep steps 1..24 and exactly **one enforceable HITL gate
at step 16**.

## Three waves

| Wave | Steps | What it is | Who pays for it |
|------|-------|------------|-----------------|
| **W1 · Foundation** | 1–10 | The planes built once per enterprise: data (Bronze/Silver/Gold), identity, runtime (MCP), ledger, HITL surface | Platform investment |
| **W2 · Pilot** | 11–18 | One scenario running end to end: trigger → orchestrate → decision-plane agents → gate → act → KPI | The first use case |
| **W3 · Scale & fuse** | 19–24 | Multi-tenant scale, fusing adjacent and cross-practice scenarios, governance at scale, feedback loops | Run-rate durable value |

## The 24 steps

Run `academy chain` to print this with the executed segment marked.

**W1 — Foundation (1–10):** SOR → Real-Time Hub ingest → Bronze landing → Tokenizer/PII →
Silver canonical → Gold semantic → MCP capability registry → Entra identities (agents *and*
personas get identities) → LEDGER store → HITL Adaptive Card surface.

**W2 — Pilot (11–18):** Event trigger → Parent orchestrator (the MAF pattern lives here) →
**Assess** agent (13) → **Classify** agent (14) → **Quantify/Compose** agent (15) →
**★ HITL gate (16)** → **Act + Evidence-Write** (17) → KPI rollup (18).

**W3 — Scale & fuse (19–24):** Scale multi-tenant → fuse adjacent scenarios → fuse
cross-practice → Purview lineage/classification at scale → LEDGER feedback loop (retraining —
this is where **Learn** lives) → Enterprise KPI.

## The six-role executable segment

This academy's runtime (`academy_core/runtime.py`) executes the W2 segment as six named roles
plus the gate:

```
ASSESS(13) → CLASSIFY(14) → QUANTIFY(15) → DECIDE(16) → ★ HITL gate(16) → ACT(17) → LEARN(23)
```

- **Assess** — read the scoped context (this employee, this case — never the table).
- **Classify** — identify what this is: which policy, which intent, which case.
- **Quantify** — compute what applies: balances, exceptions, deadlines, confidence.
- **Decide** — compose the proposal (the answer, the letter, the route). Its confidence
  feeds the gate.
- **★ HITL gate** — the one human checkpoint (see doc 04 for the four modes).
- **Act** — the only stage allowed to mutate anything, and only after the gate.
- **Learn** — close the loop: gaps, telemetry, retraining signals.

## Why W1 matters even though we mock it

Students run only W2 here, but every W2 step leans on a W1 plane: `Assess` reads a **Gold
agent-safe view** (our `data/employees.json` stands in for `gold_hr_worker_v2`); the service
adapters stand in for the **MCP capability registry**; the `Ledger` class stands in for the
ledger plane. When a chain feels easy, it's because W1 already paid the hard costs: governed
data, scoped identity, and an audit trail.
