# hr-hrsd-08 · Ticket deflection / smart routing

**Service:** HR-HRSD-04 · Ticket Deflection · **Chain:** Decide · **HITL:** ESCALATION ·
**Lead agent:** Deflection · **Personas:** Sofia Ramos (owner), Raj Patel

## What it is

When the agent can't fully resolve, the worst outcome is a **misrouted** ticket. Deflection
resolves what it can and routes the rest precisely — to the right team, with the full context
attached. This is the scenario where students watch the step-16 gate **actually fire**.

## Walkthrough

1. **ASSESS** — on an unresolved query, reads the full conversation and context.
2. **CLASSIFY** — can it resolve or must it route? KB grounding score decides
   (`RESOLVE_THRESHOLD = 0.60`).
3. **QUANTIFY** — scores confidence and picks the best destination from the routing map.
4. **DECIDE** — resolves directly, or proposes the route with a complete context package.
5. **★ ESCALATION (16)** — confidence ≥ 0.70 auto-approves; below, the run escalates to the
   routed team with everything attached. **Escalation is an outcome, not a failure.**
6. **ACT (17)** — runs only on direct resolution; on escalation the runtime routes instead.
7. **LEARN (23)** — resolve-vs-route outcomes retrain the boundary; the threshold earns trust.

## Data & tools

ServiceNow HRSD, routing map (→ `data/routing-map.json`), MCP routing tool.

## Azure AI services

Azure AI Language (classification) · Azure OpenAI (Foundry) · Microsoft Agent Framework.

## KPIs moved (synthetic reference figures)

- Ticket deflection rate — 0% → **55%** (owner: Sofia Ramos)
- Misroute rate — 23% → **<3%** (owner: Sofia Ramos)

## Run it

```bash
academy run hr-hrsd-08          # garnishment question → escalates to Payroll Operations
academy run hr-hrsd-08 --text "How many PTO days can I carry over?"   # resolves directly
academy run hr-hrsd-08 --ledger runs/escalation.jsonl                # export the evidence
```

Code: `packages/academy-scenarios-hrsd/src/academy_hrsd/hrsd08_deflection.py`

## Labs

- Run both commands above and diff the two gate rows in the ledger (Lab 3).
- There are **two** thresholds in this scenario (`RESOLVE_THRESHOLD` in the handler,
  `ESCALATION_THRESHOLD` in the runtime). Explain why they're different numbers owned by
  different layers — and what breaks if a scenario author could override the runtime's.
- Find a query that gets *misrouted* by the keyword routing map. What signal would fix it?
