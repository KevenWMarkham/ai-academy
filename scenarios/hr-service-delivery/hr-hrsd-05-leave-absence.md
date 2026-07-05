# hr-hrsd-05 · Leave & absence guidance

**Service:** HR-HRSD-02 · Life-Event Navigator · **Chain:** Classify → Decide ·
**HITL:** ZERO_TOUCH · **Lead agent:** Leave-Guide · **Personas:** Raj Patel, Sofia Ramos

## What it is

Leave is where policy complexity meets personal anxiety. The chain classifies the leave type,
grounds on the right leave policy, quantifies the employee's **actual balances and
jurisdiction benefits**, and lays out a concrete plan — options, dates and steps.

## Walkthrough

1. **ASSESS** — reads Raj's balances (PTO, sick) and jurisdiction (US-CA).
2. **CLASSIFY** — intent → leave type (caregiver, parental, medical, bereavement, vacation),
   grounded on the matching policy.
3. **QUANTIFY** — builds the option stack: 12 weeks protected caregiver leave, CA PFL 8 weeks
   concurrent, his 6 sick days, then his 14.5 PTO days.
4. **DECIDE** — the plan with pay treatment, certification deadline, and next steps, cited.
5. **★ ZERO_TOUCH (16)** — guidance is touch-free.
6. **ACT (17)** — opens a draft leave case awaiting his confirmation.
7. **LEARN (23)** — guidance-to-leave conversion tracked; confusing policies flagged.

## Data & tools

`gold_hr_worker_v2`, leave policy KB (`caregiver-medical-leave.md`, `parental-leave.md`,
`bereavement.md`), MCP leave tool.

## Azure AI services

Azure AI Language (CLU intent) · Azure AI Search · Azure OpenAI (Foundry).

## KPIs moved (synthetic reference figures)

- Leave-question deflection — 0% → **60%** (owner: Sofia Ramos)
- Employee CSAT — 3.6 → **4.5 / 5** (owner: Sofia Ramos)

## Run it

```bash
academy run hr-hrsd-05          # caring for his father after surgery
academy run hr-hrsd-05 --employee E1002 --text "I need parental leave for my second child"
```

Code: `packages/academy-scenarios-hrsd/src/academy_hrsd/hrsd05_leave_absence.py`

## Labs

- Run the second command above. Ingrid is in DE-BY — which option is *missing* from the
  QUANTIFY stack that the parental-leave policy's DE rider promises? Fix the handler.
- Why does QUANTIFY order sick days before PTO days? Find the policy sentence that dictates it.
