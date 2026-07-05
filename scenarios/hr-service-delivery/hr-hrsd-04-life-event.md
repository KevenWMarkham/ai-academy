# hr-hrsd-04 · Life-event guidance

**Service:** HR-HRSD-02 · Life-Event Navigator · **Chain:** Classify → Decide ·
**HITL:** ZERO_TOUCH · **Lead agent:** Life-Event-Navigator · **Personas:** Raj Patel, Sofia Ramos

## What it is

Major life events — a new baby, a move, a bereavement — trigger a web of HR actions employees
don't know how to navigate. The Navigator identifies every benefit, policy, and deadline the
event triggers and walks the employee through them **in deadline order**.

## Walkthrough

1. **ASSESS** — Raj signals a life event; the Navigator reads his situation and eligibility.
2. **CLASSIFY** — CLU-style intent classification maps the message to a known event type.
3. **QUANTIFY** — sequences every triggered action by its deadline (30-day leave election,
   31-day benefits window, …).
4. **DECIDE** — lays out options, dates, and next steps as a personalized plan.
5. **★ ZERO_TOUCH (16)** — guidance is touch-free; unknown events set a route instead.
6. **ACT (17)** — opens a tracking case and can kick off the tasks.
7. **LEARN (23)** — checklist drop-offs refine the flow; edge cases route to Sofia.

## Data & tools

`gold_hr_worker_v2`, benefits/policy KB, MCP life-event tool.

## Azure AI services

Azure AI Language (CLU intent) · Azure OpenAI (Foundry) · Microsoft Agent Framework.

## KPIs moved (synthetic reference figures)

- Life-event completion rate — 62% → **95%** (owner: Sofia Ramos)
- Employee CSAT — 3.6 → **4.5 / 5** (owner: Sofia Ramos)

## Run it

```bash
academy run hr-hrsd-04                                   # "We just had a baby!"
academy run hr-hrsd-04 --text "I'm moving to a new apartment next month"
```

Code: `packages/academy-scenarios-hrsd/src/academy_hrsd/hrsd04_life_event.py`

## Labs

- Add a `divorce` event: intent keywords + checklist. Which existing policy files support it,
  and which are missing?
- Lab 5 (docs/06): redesign this chain under a **Handoff** pattern for bereavements that need
  Employee Relations.
