# 06 · Student Labs

Each lab builds on the last. Labs 1–3 are read/run; 4–7 write code. The repo's gates
(`ruff check . && pytest -q`) must stay green — that is part of every grade.

## Lab 1 — Trace a run (warm-up)

Run `academy run hr-hrsd-01` and, for each ledger row, write one sentence mapping it to the
canonical step it executes (`academy chain` prints the backbone). Deliverable: a table of
step → what happened → which W1 plane it depended on.

## Lab 2 — Break the grounding

Ask hr-hrsd-01 a question the policy KB cannot answer
(`academy run hr-hrsd-01 --text "Can I expense my dog's daycare?"`). Explain: what score did
CLASSIFY produce, what did DECIDE do, what did LEARN record, and why is this *not* a failure
of the chain? Deliverable: half a page citing ledger rows.

## Lab 3 — The gate is a risk decision

Run hr-hrsd-08 twice: once with the default sample (escalates) and once with
`--text "How many PTO days can I carry over?"` (resolves). Then argue in one page: should
hr-hrsd-06 (letters) be `ZERO_TOUCH` instead of `ACK_ONLY`? Name the concrete harm scenario
that justifies your answer.

## Lab 4 — Go live with one adapter

Set `AOAI_*` env vars (or your instructor's shared endpoint) and run any scenario with
`--runtime live`. Diff the answer against mock mode. Deliverable: the diff plus two sentences
on what the LLM improved and what it was *not allowed* to change (facts, figures, citations).
Stretch: `pip install agent-framework` and use `--runtime maf`.

## Lab 5 — Design under a different MAF pattern

hr-hrsd-04 discovers mid-chain that the "life event" is a bereavement needing Employee
Relations (Aisha Bello). Sketch (diagram + one page) how the chain changes under a **Handoff**
pattern: what context transfers, where the gate sits, which KPI the ER leg moves. No code.

## Lab 6 — Implement the live Language adapter

`language.py` is mock-only by design. Implement `_classify_azure()` against the Azure AI
Language CLU REST API with the same graceful-degradation contract the other adapters follow
(env vars → try live → fall back to mock). Deliverable: the PR, with a test that passes with
no credentials set.

## Lab 7 — Ship scenario hr-hrsd-10 (capstone)

Pick a Tier-0 request not covered (holiday calendar lookup, expense-policy Q&A, org-chart
"who do I ask about X", onboarding buddy FAQ…). Ship it end to end:

1. `ScenarioSpec` with personas, KPIs (synthetic figures), Azure service seats, HITL mode —
   defend the mode in the module docstring.
2. Stage handlers for all six roles; any new synthetic data under `data/`.
3. A brief in `scenarios/hr-service-delivery/hr-hrsd-10-<name>.md` matching the house format.
4. Registration in `academy_hrsd/__init__.py` — the parametrized contract tests in
   `tests/test_chain_runtime.py` must pass **unchanged**. That's the acceptance bar: your
   scenario keeps the invariants (one gate at 16, 14-field rows, an answer for the persona).

Grading rubric: chain correctness (40%), the business case — objective→use case→persona→
chain→KPI (30%), code quality & tests (20%), the brief (10%).
