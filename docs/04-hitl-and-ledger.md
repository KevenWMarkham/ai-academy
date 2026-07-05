# 04 · HITL & the LEDGER — trust is a design surface

Two mechanisms make an agentic chain deployable in a real enterprise: a **human gate** where
consequences warrant one, and an **evidence trail** that can replay every run. Neither is
optional; both are cheap if designed in from the start.

## The step-16 HITL gate

The canonical chain has exactly **one enforceable gate**, always at step 16, between DECIDE
(the proposal) and ACT (the mutation). One gate — not zero (unaccountable), not five
(the humans become the bottleneck the chain was meant to remove).

### The four modes

| Mode | Human involvement | ACT runs when | Used by |
|------|-------------------|---------------|---------|
| `ZERO_TOUCH` | None — but every step is still evidenced | always | hr-hrsd-01/02/03/04/05/09 |
| `ACK_ONLY` | A human acknowledges the proposal (they don't redesign it) | on acknowledgment | hr-hrsd-06/07 |
| `ESCALATION` | None if confidence ≥ 0.70; below, route to a human **with full context attached** | confidence ≥ threshold | hr-hrsd-08 |
| `HITL` | A named human must approve at the Adaptive Card | on explicit approval | (heavier areas: offers, org design, comp) |

The mode is a **per-scenario risk decision**. A status lookup is a pure read — gating it would
be theater. Generating an official letter mutates the world mildly — an acknowledgment fits.
Extending a job offer moves money and people — that's a hard `HITL` gate (see the Talent
Acquisition area in the production platform).

### What students should notice in the code

`ChainRunner._gate()` (`academy_core/runtime.py`) is ~30 lines and enforces all four modes.
Notice: **ACT is structurally unreachable without an approved gate** — the runtime, not the
scenario author, guarantees it. An escalated run still completes LEARN and the KPI rollup;
escalation is an outcome, not a failure.

## The 14-field LEDGER row

Every executed step appends one row (`academy_core/ledger.py`):

| # | Field | Why it exists |
|---|-------|---------------|
| 1 | `run_id` | one chain execution |
| 2 | `seq` | replay order |
| 3 | `timestamp` | when (UTC) |
| 4 | `scenario_id` | which scenario |
| 5 | `step` | canonical 1..24 step number |
| 6 | `stage` | role name / `hitl-gate` / `trigger` / `orchestrate` / `kpi-rollup` |
| 7 | `agent` | which agent acted |
| 8 | `persona` | who the step served |
| 9 | `action` | short verb phrase |
| 10 | `detail` | human-readable evidence |
| 11 | `confidence` | if the stage produced one |
| 12 | `hitl_mode` | the scenario's gate contract |
| 13 | `actor` | `system` or the human at the gate |
| 14 | `outcome` | ok / approved / acknowledged / escalated / skipped / pending |

Export any run's evidence: `academy run hr-hrsd-08 --ledger runs/escalation.jsonl`.

## The teaching claim

The ledger is not compliance overhead — it is the **feedback substrate**. Step 23 (LEARN)
reads ledger outcomes to retrain the resolve-vs-route boundary, surface KB gaps, and find
process bottlenecks. The same rows that satisfy the auditor improve the model. Design the
evidence once, use it twice.
