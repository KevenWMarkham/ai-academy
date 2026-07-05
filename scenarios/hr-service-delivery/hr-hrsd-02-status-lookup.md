# hr-hrsd-02 · Status lookup

**Service:** HR-HRSD-01 · Policy Q&A Copilot · **Chain:** Assess · **HITL:** ZERO_TOUCH ·
**Lead agent:** Status-Lookup · **Persona:** Raj Patel

## What it is

"Where's my request?" is a top ticket driver. Status-Lookup answers it instantly across cases,
requests and approvals — scoped strictly to what the employee is allowed to see. A pure read:
the cheapest possible chain, and a masterclass in why not everything needs an LLM.

## Walkthrough

1. **ASSESS** — reads the cases visible to Raj (and only Raj) from `gold_hr_case_v1`.
2. **CLASSIFY** — identifies *which* request he means and its current stage.
3. **DECIDE** — status, owner, and expected date; disambiguates if several match.
4. **★ ZERO_TOUCH (16)** — a pure read; no human needed, nothing to approve.
5. **ACT (17)** — delivered in Teams; no mutation of anything.
6. **LEARN (23)** — stuck items (>7 days in one stage) ping their owner; lookup patterns
   surface process bottlenecks.

## Data & tools

ServiceNow HRSD, `gold_hr_case_v1` (→ `data/cases.json`), MCP status tool.

## Azure AI services

Azure OpenAI (Foundry) · Microsoft Agent Framework.

## KPIs moved (synthetic reference figures)

- Status-ticket volume — high → **-70%** (owner: Sofia Ramos)
- Average handle time — 2 days → **2 min** (owner: Raj Patel)

## Run it

```bash
academy run hr-hrsd-02          # finds Raj's tuition reimbursement case
```

Code: `packages/academy-scenarios-hrsd/src/academy_hrsd/hrsd02_status_lookup.py`

## Labs

- The chain skips QUANTIFY entirely. Is that legitimate? Check what the contract tests actually
  require, and defend the omission in two sentences.
- Change `STUCK_AFTER_DAYS` to 3 and predict the LEARN row for case HRC-20431 before running.
