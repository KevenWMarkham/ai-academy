# hr-hrsd-07 · Data-correction request intake

**Service:** HR-HRSD-03 · Letter & Doc Generation · **Chain:** Act · **HITL:** ACK_ONLY ·
**Lead agent:** Data-Correction · **Personas:** Raj Patel & Sofia Ramos

## What it is

Bad worker data poisons every downstream chain (hr-hrsd-06 blocks on it). This scenario turns
a free-text complaint into a **structured, routed correction**: detect the PII, identify the
field, capture current→proposed, route to the owning data team.

## Walkthrough

1. **ASSESS** — reads Raj's current record values for comparison, scoped.
2. **CLASSIFY** — identifies the correction target (address / name / bank details) and detects
   the PII entities in the message (tokenizer-plane discipline, canonical step 4).
3. **QUANTIFY** — structures the change: field, current value, proposed value.
4. **DECIDE** — the correction proposal, routed to the owning team with its SLA.
5. **★ ACK_ONLY (16)** — Raj confirms exactly what will change before anything is filed.
6. **ACT (17)** — the correction case is filed; status flows back via hr-hrsd-02.
7. **LEARN (23)** — correction frequency by field feeds data-quality dashboards; chronic
   offenders get fixed at the source system.

## Data & tools

`gold_hr_case_v1`, ServiceNow HRSD, routing map (→ `data/routing-map.json`), MCP intake tool.

## Azure AI services

Azure AI Language (PII detection / NER) · Azure OpenAI (Foundry).

## KPIs moved (synthetic reference figures)

- Intake SLA adherence — 71% → **98%** (owner: Sofia Ramos)
- Intake consistency — low → **100% structured** (owner: Sofia Ramos)

## Run it

```bash
academy run hr-hrsd-07          # wrong address, new one extracted from the message
```

Code: `packages/academy-scenarios-hrsd/src/academy_hrsd/hrsd07_data_correction.py`

## Labs

- Try `--text "my bank account ending 4471 is wrong"` — where does the PII regex fall short of
  Azure AI Language's NER, and what would the live adapter (Lab 6) catch?
- Why must this scenario *never* be ZERO_TOUCH, even though the change seems small? Name the
  attack it would enable.
