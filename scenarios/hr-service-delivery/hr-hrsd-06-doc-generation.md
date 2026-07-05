# hr-hrsd-06 · Letter & document generation

**Service:** HR-HRSD-03 · Letter & Doc Generation · **Chain:** Act · **HITL:** ACK_ONLY ·
**Lead agent:** Doc-Gen · **Personas:** Raj Patel & Sofia Ramos

## What it is

Employment letters, verifications, leave confirmations — high volume, fully templated, yet
still manual in most HR shops. Doc-Gen produces them personalized and jurisdiction-correct,
on demand. First scenario where ACT **mutates the world**, so the gate steps up to ACK_ONLY.

## Walkthrough

1. **ASSESS** — reads only the fields the template needs from Raj's record, scoped.
2. **CLASSIFY** — selects the right template and jurisdiction-correct language.
3. **QUANTIFY** — validates the data is **complete and current**; missing fields block the
   draft and point to hr-hrsd-07 (data correction) first.
4. **DECIDE** — drafts the personalized document for review.
5. **★ ACK_ONLY (16)** — Raj (or Sofia for official letters) acknowledges; the human
   confirms, they don't redesign.
6. **ACT (17)** — generated, delivered in Teams, logged to the Purview audit trail.
7. **LEARN (23)** — request volume by letter type informs self-service expansion.

## Data & tools

`gold_hr_worker_v2`, letter templates (→ `data/letter-templates/`), MCP doc-gen tool,
Purview audit.

## Azure AI services

Azure OpenAI (Foundry) · Azure AI Document Intelligence (inbound side) · Microsoft Purview.

## KPIs moved (synthetic reference figures)

- Document turnaround — 3 days → **instant** (owner: Sofia Ramos)
- Self-serve rate — 5% → **80%** (owner: Sofia Ramos)

## Run it

```bash
academy run hr-hrsd-06          # employment verification for a mortgage application
```

Code: `packages/academy-scenarios-hrsd/src/academy_hrsd/hrsd06_doc_generation.py`

## Labs

- Delete `salary_band` from Raj's record in `data/employees.json` and run again. Trace how
  QUANTIFY blocks DECIDE, then restore the data.
- The teaching claim is "letter generation is a data-completeness problem before it is a
  generation problem." Argue for or against in one paragraph, citing the walkthrough.
- Add a third template (e.g. visa-support letter) end to end.
