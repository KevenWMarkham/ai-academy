# hr-hrsd-09 · Multilingual employee support

**Service:** HR-HRSD-04 · Ticket Deflection · **Chain:** Classify · **HITL:** ZERO_TOUCH ·
**Lead agent:** Multilingual · **Personas:** Lucía Álvarez (asks), Sofia Ramos (owns KPIs)

## What it is

The same grounded answers, in the employee's own language. Translator **wraps** the chain:
detect the language, translate in, run the identical grounded answer path, translate out.
The chain itself is language-agnostic — that's the teaching point.

## Walkthrough

1. **ASSESS** — detects the message language (es); reads Lucía's record and preference.
2. **CLASSIFY** — translates es→en for processing; classifies the intent (pto_balance).
3. **QUANTIFY** — grounds on the PTO policy; reads her personal balance from the worker record.
4. **DECIDE** — composes the grounded English answer, then translates it back en→es.
5. **★ ZERO_TOUCH (16)** — a standard question in any language stays touch-free.
6. **ACT (17)** — delivered in Teams in Spanish — her language, not the company's.
7. **LEARN (23)** — the language mix of inbound questions steers which policies get
   human-reviewed translations next.

## Data & tools

`gold_hr_worker_v2`, policy KB, MCP translate tool.

## Azure AI services

Azure AI Translator · Azure AI Language (detection) · Azure OpenAI (Foundry).

## KPIs moved (synthetic reference figures)

- Non-English deflection rate — 0% → **50%** (owner: Sofia Ramos)
- Employee CSAT (non-English) — 3.1 → **4.5 / 5** (owner: Sofia Ramos)

## Run it

```bash
academy run hr-hrsd-09          # "¿Cuántos días de vacaciones me quedan este año?"
```

In mock mode the translation hops are visibly tagged (`[en→es] …`) — the adapter is honest
about being a mock. Set `AZURE_TRANSLATOR_KEY` and `--runtime live` for real translation.

Code: `packages/academy-scenarios-hrsd/src/academy_hrsd/hrsd09_multilingual.py`

## Labs

- Ask in German as Ingrid (`--employee E1002 --text "Wieviele Urlaubstage habe ich noch und bitte schnell"`).
  Does detection fire? Read `_LANGUAGE_MARKERS` and explain the two-marker rule.
- Why translate-then-ground instead of maintaining a Spanish policy KB? Give one argument each
  way, and say which the LEARN stage's telemetry would eventually settle.
