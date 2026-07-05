# 02 · MAF Orchestration Patterns — step 12 is a choice

At canonical step 12, the parent orchestrator dispatches agents. **How** it dispatches them is
the Microsoft Agent Framework (MAF) orchestration pattern — and choosing the right pattern per
HR area is a design decision students must be able to defend.

## The five patterns

| Pattern | Shape | Choose when | HR area that uses it |
|---------|-------|-------------|----------------------|
| **Sequential** | A → B → C, one baton | The work is a known pipeline; each step needs the last step's output | **HR Service Delivery (this academy)**, Onboarding, Offboarding |
| **Concurrent** | A ∥ B ∥ C, fan-out/fan-in | Independent sub-tasks whose results merge | Learning & Skills (12 scenarios) |
| **Group Chat** | Agents debate on a shared thread, a manager arbitrates | The answer benefits from multiple perspectives challenging each other | Performance & Goals |
| **Handoff** | A works until it decides B owns it, then transfers control | Distinct ownership phases with clean transfer of context | Talent Acquisition (recruiter agent → hiring-manager agent), Employee Relations |
| **Magentic** | A manager agent decomposes an open-ended ask on the fly | The questions are not pre-scripted; the task graph is discovered at runtime | Workforce Planning (executive what-if) |

## Why HR Service Delivery is Sequential

Tier-0 requests are short, high-volume, and well-understood: read context → ground → check
exceptions → answer. A single grounded agent walking a fixed pipeline is the cheapest thing
that works, and cheap matters at help-desk volume. The sophistication budget goes to
**grounding** (the right policy, the right worker record) and the **gate**, not to exotic
coordination.

Rule of thumb: *pick the least coordination the use case survives.* Every pattern step up
(Sequential → Concurrent → Group Chat → Handoff → Magentic) buys flexibility with latency,
cost, and explainability.

## Where MAF appears in this repo

- `packages/academy-services/src/academy_services/maf.py` — builds a real MAF `Agent` on Azure
  OpenAI (Foundry) when `ACADEMY_RUNTIME=maf` and `agent-framework` is installed. Mirrors the
  production pattern in `scenario_chain/maf.py`.
- `ChainRunner` (`academy_core/runtime.py`) plays the **parent orchestrator** (step 12) with a
  hard-coded Sequential dispatch — deliberately simple so students can read it.
- The production system exposes tools to agents via an **MCP server** (`MCPStdioTool` in MAF);
  our `ServiceHub` is the teaching stand-in for that capability registry.

## Lab pointer

Lab 5 (doc 06) asks you to sketch how hr-hrsd-04 (life events) would change under a **Handoff**
pattern when an event turns out to be a bereavement that needs Employee Relations — that's a
real fusion of HR areas (canonical step 20).
