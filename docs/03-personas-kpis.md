# 03 · Personas → KPIs — who owns the outcome

A chain without a named KPI owner is a tech demo. Every scenario names the personas it serves
and the KPIs it moves — and the KPI table is what the CHRO sees at canonical step 24.

> All baseline/target figures are **synthetic reference figures** for teaching — never client
> claims.

## The persona roster

Ten personas recur across the nine HR areas. Every one of them meets the platform **only
through a Copilot surface** — never the agents, the schema, or the ledger directly. (Roster
code: `academy_core/personas.py`.)

| Persona | Role | Home in HR | Copilot surface |
|---------|------|-----------|-----------------|
| Maya Chen | Talent Acquisition Partner | Recruiting | Copilot Studio agent |
| David Okafor | Hiring / People Manager | Across the business | Copilot in Teams |
| **Raj Patel** | **Employee / New Hire** | **Front line** | **Copilot in Teams** |
| Priya Sharma | HR Business Partner | Embedded in the business | Copilot in Teams |
| **Sofia Ramos** | **HR Operations Specialist** | **HR shared services** | **custom Copilot / HRSD** |
| Aisha Bello | Employee Relations Specialist | ER & compliance | Copilot Studio agent |
| Marcus Lee | Total Rewards / Comp Analyst | Comp & Benefits | custom Copilot |
| Nina Kowalski | L&D Lead | Talent / L&D | Copilot + Viva Learning |
| Tom Becker | People Analytics Lead | People Analytics | Power BI + Copilot |
| Elena Vasquez | CHRO | Executive | Power BI + Copilot |

**Raj** (the asker) and **Sofia** (the owner of the help-desk KPIs, and the escalation
destination) carry the HR Service Delivery area.

## The area KPI table

Run `academy kpi` for the full per-scenario table. The four headline KPIs:

| Persona | KPI owned | Baseline → Target | How the chain moves it |
|---------|-----------|-------------------|------------------------|
| Sofia (HR Ops) | Ticket deflection rate | 0% → **55%** | grounded self-service in Teams |
| Sofia (HR Ops) | First-contact resolution | 61% → **89%** | single grounded agent |
| Raj (Employee) | Average handle time | 2 days → **2 min** | instant answers & docs |
| Sofia (HR Ops) | Employee CSAT | 3.6 → **4.5 / 5** | fast, accurate, 24×7 |

## The attribution discipline

Step 18 (KPI rollup) writes a ledger row naming the KPIs each run moves. That's the discipline:
**every run must say which needle it moved**. When a run escalates (hr-hrsd-08 below the
confidence threshold), that run *still* moves the misroute-rate KPI — routing precisely with
context attached is the value, not just avoiding humans.

## Writing a business case from this repo

Objective → use case → persona → chain → KPI, one line each. Example:

> *Cut HR ticket load* (objective) by answering policy questions at Tier-0 (use case hr-hrsd-01)
> for every employee like Raj (persona), with a Sequential grounded chain at ZERO_TOUCH (chain),
> moving ticket deflection 0%→55% and first-contact resolution 61%→89% for Sofia's team (KPIs).

If you cannot fill in all five slots, the scenario isn't ready to build.
