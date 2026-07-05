# hr-hrsd-01 · Policy Q&A

**Service:** HR-HRSD-01 · Policy Q&A Copilot · **Chain:** Classify · **HITL:** ZERO_TOUCH ·
**Lead agent:** Policy-QA · **Personas:** Raj Patel (asks), Sofia Ramos (owns KPIs)

## What it is

Most HR tickets are policy questions with a known answer. Policy-QA answers them instantly in
Teams — grounded on the actual policy **and** the employee's own context — before a ticket is
ever raised.

## Walkthrough

1. **ASSESS** — Raj asks a policy question; Policy-QA reads his worker context, scoped to him only.
2. **CLASSIFY** — grounds the answer on the correct policy and jurisdiction (AI Search over the KB).
3. **QUANTIFY** — checks for exceptions that apply specifically to him (his US-CA rider, his balance).
4. **DECIDE** — composes a precise, **cited** answer; retrieval score becomes the confidence.
5. **★ ZERO_TOUCH (16)** — no human needed for a standard question; fully evidenced.
6. **ACT (17)** — answer delivered in Teams; no ticket raised.
7. **LEARN (23)** — unanswered questions surface knowledge-base gaps to Sofia.

## Data & tools

`gold_hr_worker_v2` (→ `data/employees.json`), policy KB (→ `data/kb/`), MCP policy-QA tool.

## Azure AI services

Azure OpenAI (Foundry) · Azure AI Search · Microsoft Agent Framework.

## KPIs moved (synthetic reference figures)

- Ticket deflection rate — 0% → **55%** (owner: Sofia Ramos)
- First-contact resolution — 61% → **89%** (owner: Sofia Ramos)

## Run it

```bash
academy run hr-hrsd-01
academy run hr-hrsd-01 --text "Can I cash out unused PTO when I leave?"
```

Code: `packages/academy-scenarios-hrsd/src/academy_hrsd/hrsd01_policy_qa.py`

## Labs

- Trace every ledger row to its canonical step (Lab 1).
- Ask an unanswerable question and explain the LEARN row (Lab 2).
- Why does the citation (`[source: pto]`) matter more than answer fluency? One paragraph.
