# 05 · Azure AI Services Map — which service powers which scenario

An AI service is a *capability seat* inside a chain, never the product. This map shows which
seat each Azure AI service fills across the nine scenarios, and where the adapter lives in
`packages/academy-services/`.

## Service → seat → scenarios

| Azure AI service | Seat in the chain | Adapter | Scenarios |
|------------------|-------------------|---------|-----------|
| **Azure OpenAI (Foundry)** | DECIDE — polish the grounded draft into prose | `foundry.py` | all 9 |
| **Microsoft Agent Framework (MAF)** | Step 12 orchestration; the agent runtime | `maf.py` | all 9 (`ACADEMY_RUNTIME=maf`) |
| **Azure AI Search** | CLASSIFY — grounded retrieval over the policy KB | `search.py` | 01, 03, 05, 08, 09 |
| **Azure AI Language** | CLASSIFY — intent (CLU), language detection, PII/NER | `language.py` | 04, 05, 06, 07, 08, 09 |
| **Azure AI Translator** | wraps the chain — translate in, translate out | `translator.py` | 09 |
| **Azure AI Document Intelligence** | inbound documents → structured fields | `documents.py` (outbound side mocked) | 06, 07 |
| **Microsoft Purview** | governance plane — audit, lineage, PII labels | (concept; logged in ledger detail) | 06, 07, all via step 22 |
| **Microsoft Entra** | identity plane — agent + persona identities | (concept; W1 step 8) | all |

## The mock-first contract

Every adapter follows the same discipline, worth internalizing:

1. **Mock is the default** and is deterministic — no credentials, no network, same output
   every run. CI and graded labs depend on this.
2. **Live is opt-in per adapter** — `ACADEMY_RUNTIME=live` plus that service's env vars.
3. **Degradation is graceful** — a missing SDK, expired key, or thrown exception falls back
   to mock. A half-configured lab machine still teaches.

The mock also teaches the service's *shape*: `PolicySearch` returns scored hits with snippets
(what AI Search returns), `LanguageService.classify_intent` returns intent + confidence +
evidence (what CLU returns), the mock translator visibly tags the language hop. Students learn
the integration contract before they ever spend a token.

## Where the LLM does — and does not — sit

Deliberate design decision, visible in every scenario's DECIDE handler: the chain composes its
facts **deterministically** (balances from the worker record, citations from search, deadlines
from the checklist), then hands the LLM a **draft to polish** — not an open question.

- Grounding failures are search problems, not hallucinations.
- The gate's confidence number comes from retrieval/classification scores, not model vibes.
- Mock mode (polish = identity function) proves the chain works with the LLM removed.

If the answer is wrong with the LLM removed, the chain is wrong. Fix the chain.

## Relationship to the AI-Services repo

`C:\code\AI-Services` holds standalone demos (Azure Map, Document Intelligence, Language,
Speech). Those show each service solo; this repo shows the same services **composed into
chains** with personas, gates, and KPIs. Lab 6 asks you to promote one AI-Services demo into
a new scenario here.
