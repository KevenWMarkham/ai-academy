# HR Service Delivery (Tier-0) — Scenario Briefs

The everyday HR help desk, answered in Teams before a ticket is ever raised. Area pattern:
a single grounded agent on a short **Sequential** MAF chain at **ZERO_TOUCH**, escalating only
the genuine edge cases. Personas: **Raj Patel** (employee) asks; **Sofia Ramos** (HR Ops) owns
the KPIs and catches the escalations.

One brief per scenario; code lives in `packages/academy-scenarios-hrsd/`.

| Brief | Service group | Chain | HITL |
|-------|---------------|-------|------|
| [hr-hrsd-01 · Policy Q&A](hr-hrsd-01-policy-qa.md) | Policy Q&A Copilot | Classify | ZERO_TOUCH |
| [hr-hrsd-02 · Status lookup](hr-hrsd-02-status-lookup.md) | Policy Q&A Copilot | Assess | ZERO_TOUCH |
| [hr-hrsd-03 · HR knowledge-base search](hr-hrsd-03-kb-search.md) | Policy Q&A Copilot | Classify | ZERO_TOUCH |
| [hr-hrsd-04 · Life-event guidance](hr-hrsd-04-life-event.md) | Life-Event Navigator | Classify → Decide | ZERO_TOUCH |
| [hr-hrsd-05 · Leave & absence guidance](hr-hrsd-05-leave-absence.md) | Life-Event Navigator | Classify → Decide | ZERO_TOUCH |
| [hr-hrsd-06 · Letter & document generation](hr-hrsd-06-doc-generation.md) | Letter & Doc Generation | Act | ACK_ONLY |
| [hr-hrsd-07 · Data-correction request intake](hr-hrsd-07-data-correction.md) | Letter & Doc Generation | Act | ACK_ONLY |
| [hr-hrsd-08 · Ticket deflection / smart routing](hr-hrsd-08-deflection.md) | Ticket Deflection | Decide | ESCALATION |
| [hr-hrsd-09 · Multilingual employee support](hr-hrsd-09-multilingual.md) | Ticket Deflection | Classify | ZERO_TOUCH |

**Brief format** (also the required format for the Lab 7 capstone): What it is · Walkthrough
(six roles + gate) · Data & tools · Azure AI services · KPIs moved · Run it · Labs.
