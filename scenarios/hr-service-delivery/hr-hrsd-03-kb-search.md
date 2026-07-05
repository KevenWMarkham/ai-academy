# hr-hrsd-03 · HR knowledge-base search

**Service:** HR-HRSD-01 · Policy Q&A Copilot · **Chain:** Classify · **HITL:** ZERO_TOUCH ·
**Lead agent:** KB-Search · **Personas:** Raj Patel, Sofia Ramos

## What it is

Not question-answering: **ranked, cited retrieval** when the employee wants the source itself.
The Classify role *is* the product — this scenario isolates grounded search so students see
it apart from generation.

## Walkthrough

1. **ASSESS** — search scope limited to documents Raj may read (jurisdiction-aware).
2. **CLASSIFY** — hybrid retrieval over the policy KB; ranked hits with scores and snippets.
3. **DECIDE** — a ranked, cited result list (top 3), each with the matching passage.
4. **★ ZERO_TOUCH (16)** — nothing to approve; retrieval is read-only.
5. **ACT (17)** — list delivered in Teams with open-document links.
6. **LEARN (23)** — zero-hit queries are logged as KB gaps; query→click signals tune ranking.

## Data & tools

The knowledge base (→ `data/kb/`: policies, guides, FAQs, localized docs — each chunked and
embeddable, see docs/08), MCP search tool.

## Azure AI services

Azure AI Search (hybrid/semantic) · Azure OpenAI embeddings.

## KPIs moved (synthetic reference figures)

- Search success rate — 48% → **85%** (owner: Sofia Ramos)
- Ticket deflection rate — 0% → **55%** (owner: Sofia Ramos)

## Run it

```bash
academy run hr-hrsd-03          # "home office equipment stipend" → Remote & Hybrid Work Policy
```

Code: `packages/academy-scenarios-hrsd/src/academy_hrsd/hrsd03_kb_search.py`

## Labs

- Read `KBSearch._query_local` (~30 lines). Which query would rank the *wrong* policy
  first? Construct one, verify it, and explain what Azure AI Search's semantic ranker would
  do differently.
- Compare `academy kb search "time away when my mother is ill"` with and without `--vector`.
  The mock embedding is *soft-lexical* (feature-hashed) — explain why its ranking differs from
  keyword's, and what a live semantic embedding would do differently (docs/08, Lab 3).
- What distinguishes this scenario from hr-hrsd-01 in one sentence? (Hint: who does the reading.)
