# AI Academy — HR Service Delivery Scenario Chains

A teaching monorepo for an academic setting: students learn how **agentic services built on the
Microsoft Agent Framework (MAF)**, composed into **scenario chains**, produce **live business
outcomes** — use cases, tied to personas, moving named KPIs — at enterprise scale.

The worked domain is **HR Service Delivery (Tier-0)**: the everyday HR help desk — policy
questions, life events, letters, status lookups — answered in Teams before a ticket is ever
raised. A single grounded agent runs a short **Sequential** chain at **ZERO_TOUCH**, escalating
only the genuine edge cases.

> Every scenario here runs the same canonical chain backbone with a single enforceable
> human-in-the-loop (HITL) gate at **step 16**, and writes a **14-field LEDGER row** per step.
> All currency / ROI / KPI figures are **synthetic reference figures** — never client claims.

---

## The core idea students should leave with

```
Business objective  →  Use case  →  Persona  →  Scenario chain  →  KPI moved
"cut HR ticket load"   policy Q&A    Raj (employee)   Assess→Classify→      ticket deflection
                                     Sofia (HR Ops)   Quantify→Decide→      0% → 55%
                                                      ★HITL(16)→Act→Learn
```

An **AI service** (Azure OpenAI, AI Search, AI Language, Translator, Document Intelligence) is
never the product. The product is the **chain**: agents in named roles, grounded on governed
data, gated by a human where it matters, leaving evidence in a ledger, rolling up to a KPI a
named persona owns.

## Repo map

```
AI-Academy/
├── README.md                     ← you are here
├── pyproject.toml                ← uv workspace root
├── docs/                         ← the curriculum
│   ├── 01-scenario-chains.md     ← the canonical 24-step chain (W1/W2/W3)
│   ├── 02-maf-patterns.md        ← MAF orchestration patterns (Sequential, Handoff, Magentic…)
│   ├── 03-personas-kpis.md       ← the HR persona roster and the KPIs they own
│   ├── 04-hitl-and-ledger.md     ← HITL modes, the step-16 gate, the 14-field ledger
│   ├── 05-azure-ai-services-map.md ← which Azure AI service powers which scenario
│   ├── 06-student-labs.md        ← graded lab exercises
│   ├── 07-m365-copilot-surface.md ← surface in M365 Copilot: Deloitte-tenant test → customer deploy
│   └── 08-knowledge-base.md      ← the KB corpus, vector pipeline, Azure AI Search index
├── packages/
│   ├── academy-core/             ← chain runtime: roles, HITL gate, ledger, KPI rollup
│   ├── academy-services/         ← AI-service adapters (mock-first, live-Azure optional)
│   └── academy-scenarios-hrsd/   ← the 9 HR Service Delivery scenarios (runnable)
├── apps/
│   ├── academy-cli/              ← `academy` command: list / show / run / chain / kpi
│   ├── academy-api/              ← FastAPI backend (M365 Copilot agent + dashboard)
│   └── academy-web/              ← React dashboard: run chains, watch the gate & ledger live
├── m365/
│   ├── appPackage/               ← declarative agent (v1.7) + API plugin (v2.4) + OpenAPI
│   └── package.ps1               ← stamps the API URL, zips the uploadable package
├── infra/                        ← Bicep + deploy.ps1: API on Azure Container Apps
├── scenarios/
│   └── hr-service-delivery/      ← one teaching brief per scenario (hr-hrsd-01 … 09)
├── data/
│   ├── kb/                       ← 30-doc synthetic knowledge base (policies/guides/faq/localized)
│   │                                chunked + embeddable → Azure AI Search (`academy kb push`)
│   └── …                         ← employees, cases, routing map, letter templates
└── tests/                        ← every scenario runs end-to-end in CI, mock mode
```

## The 9 scenarios

| ID | Scenario | Service | Chain | HITL | Lead agent |
|----|----------|---------|-------|------|------------|
| hr-hrsd-01 | Policy Q&A | Policy Q&A Copilot | Classify | ZERO_TOUCH | Policy-QA |
| hr-hrsd-02 | Status lookup | Policy Q&A Copilot | Assess | ZERO_TOUCH | Status-Lookup |
| hr-hrsd-03 | HR knowledge-base search | Policy Q&A Copilot | Classify | ZERO_TOUCH | KB-Search |
| hr-hrsd-04 | Life-event guidance | Life-Event Navigator | Classify → Decide | ZERO_TOUCH | Life-Event-Navigator |
| hr-hrsd-05 | Leave & absence guidance | Life-Event Navigator | Classify → Decide | ZERO_TOUCH | Leave-Guide |
| hr-hrsd-06 | Letter & document generation | Letter & Doc Generation | Act | ACK_ONLY | Doc-Gen |
| hr-hrsd-07 | Data-correction request intake | Letter & Doc Generation | Act | ACK_ONLY | Data-Correction |
| hr-hrsd-08 | Ticket deflection / smart routing | Ticket Deflection | Decide | ESCALATION | Deflection |
| hr-hrsd-09 | Multilingual employee support | Ticket Deflection | Classify | ZERO_TOUCH | Multilingual |

Full briefs (use case, walkthrough, KPIs, labs) live in
[scenarios/hr-service-delivery/](scenarios/hr-service-delivery/README.md).

## Quickstart

Everything runs **without any Azure credentials** — the service adapters ship with deterministic
mock implementations so the chains are fully observable offline. Python 3.11+.

```bash
# with uv (recommended)
uv sync
uv run academy list
uv run academy run hr-hrsd-01

# or with plain pip
py -m venv .venv && .venv\Scripts\Activate.ps1        # Windows
pip install -e packages/academy-core -e packages/academy-services \
            -e packages/academy-scenarios-hrsd -e apps/academy-cli pytest
academy list
academy run hr-hrsd-01
```

Try the interesting paths:

```bash
academy run hr-hrsd-08          # low confidence → the ESCALATION gate routes to Sofia (HR Ops)
academy run hr-hrsd-06          # ACK_ONLY — a human acknowledges before the letter is generated
academy run hr-hrsd-09          # Spanish in, Spanish out — Translator wraps the chain
academy chain                   # print the canonical 24-step chain
academy run hr-hrsd-01 --text "Can I cash out unused PTO when I leave?"
```

## The dashboard

A React console (Vite + TypeScript) over the same API the Copilot agent uses — pick a
scenario from the register, ask as Raj/Ingrid/Lucía, and watch the chain execute: the
stage-by-stage **ledger register**, the **stamped gate verdict** (approved / escalated /
pending), the answer as delivered in Teams, and the KPIs the run moves.

```bash
npm install
npm run dev        # api on :8000 + web on :5173 (proxied, no CORS config needed)
```

## Going live (optional)

Copy [.env.example](.env.example) to `.env` and set Azure OpenAI / AI Search / Translator /
Language credentials, then run with `ACADEMY_RUNTIME=live` (direct SDK calls) or
`ACADEMY_RUNTIME=maf` (a real MAF `Agent` on Foundry — `pip install agent-framework`). Adapters
degrade gracefully: missing creds or SDKs fall back to mock, so a half-configured lab machine
still works.

## Surfacing in M365 Copilot

The end state is Raj asking these questions **inside Copilot**. The repo ships the whole
surface: a declarative agent ([m365/appPackage/](m365/appPackage/manifest.json)) whose action
is an API plugin calling [apps/academy-api](apps/academy-api/src/academy_api/main.py), deployed
to Azure Container Apps ([infra/](infra/main.bicep)). Lifecycle: **test on the Deloitte tenant
(synthetic data, API-key auth) → deploy at the customer site (their Azure, Entra auth)** —
only the base URL and the auth block change in the package. Full runbook:
[docs/07-m365-copilot-surface.md](docs/07-m365-copilot-surface.md).

```powershell
infra/deploy.ps1 -ResourceGroup rg-ai-academy-test -ApiKey "<key>"   # Deloitte tenant Azure
python scripts/make_icons.py                                          # once
m365/package.ps1 -ApiBaseUrl https://<aca-fqdn>                       # → sideload the zip
```

## Learning path

1. Read [docs/01-scenario-chains.md](docs/01-scenario-chains.md) — the chain is the unit of value, not the model.
2. Read [docs/03-personas-kpis.md](docs/03-personas-kpis.md) — who owns the outcome.
3. Run `academy run hr-hrsd-01` and read the stage-by-stage trace against the brief.
4. Read the runtime ([packages/academy-core/src/academy_core/runtime.py](packages/academy-core/src/academy_core/runtime.py)) — ~200 lines, the whole engine.
5. Do the labs in [docs/06-student-labs.md](docs/06-student-labs.md) — ending with *write scenario hr-hrsd-10*.

## Relationship to sibling repos

- **`C:\code\scenario_chain`** — the production seller-enablement platform this academy distills;
  the canonical 24-step chain and the MAF runtime pattern come from there.
- **`C:\code\AI-Services`** — per-service demos (Azure Map, Document Intelligence, Language,
  Speech); this repo shows how those *individual* services compose into *chains*.

## Gates

```bash
ruff check . && pytest -q
```
