# 08 · The Knowledge Base — corpus, vectors, and Azure AI Search

Grounding quality is the ceiling on every chain's answer quality. This doc covers the KB that
sets that ceiling: a governed synthetic corpus, a chunk-and-embed pipeline with a **vector
search column**, and the Azure AI Search index it ships to.

## The corpus (`data/kb/`)

30 synthetic documents — reviewed against all nine scenarios so each has grounding:

| Folder | Contents | Grounds |
|--------|----------|---------|
| `policies/` (15) | PTO, parental, caregiver/medical, bereavement, sick, holidays, jury/civic, remote work, tuition, benefits enrollment, health plans, 401(k), expenses, accommodations, relocation | hr-hrsd-01/03/05 and the life-event chains |
| `guides/` (10) | how-to (time off, status, letters, data correction), life-event guides (new child, marriage, moving, bereavement), payslips, when-to-contact-HR | hr-hrsd-02/04/06/07/08 |
| `faq/` (3) | leave, benefits, HR services | hr-hrsd-03/08 |
| `localized/` (2) | es + de PTO summaries | hr-hrsd-09 |

Every document carries frontmatter — the governance metadata that becomes index filters:

```yaml
---
title: Paid Time Off (PTO) Policy
doc_type: policy            # policy | guide | faq
category: time-off
jurisdictions: [GLOBAL, US-CA, DE-BY]
language: en                # retrieval filters to the employee's language
scenarios: [hr-hrsd-01, hr-hrsd-03, hr-hrsd-05, hr-hrsd-09]   # what this doc grounds
---
```

`academy kb stats` prints the corpus and the **per-scenario coverage table**; a test fails if
any scenario loses its grounding documents.

### Two deliberate gaps

- **Garnishment / court-ordered pay topics are NOT in the KB.** hr-hrsd-08's teaching moment
  is the escalation gate firing on an ungroundable request — a regression test keeps it out.
- Sensitive topics (ER complaints, comp disputes) appear only in *when-to-contact-hr* as
  route-to-a-human entries — deliberately not self-service.

## The pipeline: chunk → embed → index

```
data/kb/**/*.md ──chunker──▶ KbChunk records ──embedder──▶ content_vector ──▶ Azure AI Search
   (frontmatter)   (## sections)  (id, metadata, text)  (256 or 1536 dims)     (HNSW index)
```

- **Chunker** (`academy_services/kb.py`) — splits each document at its `##` sections; each
  chunk keeps the document's metadata plus its own `section` label. ~95 chunks from 30 docs.
- **Embedder** (`embeddings.py`) — the vector column. Two modes, one interface:
  - *mock (default)*: deterministic 256-dim **feature-hashing embedding** (token → signed
    slot, L2-normalized). Cosine similarity works offline, tests are reproducible, students
    run real vector search with zero credentials.
  - *live*: Azure OpenAI `text-embedding-3-small` (1536 dims) when `AOAI_EMBED_DEPLOYMENT`
    is set — same code path, real semantics.
- **Build** — `academy kb build --vectors` writes `data/kb/index/chunks.jsonl`, one record
  per chunk with its `content_vector` — exactly what gets uploaded to the index.

## Retrieval modes (`search.py` — one adapter, three strategies)

| Mode | How | When |
|------|-----|------|
| Local keyword | fraction of query terms matched, title-weighted, best chunk per doc | default; deterministic, explainable, drives all tests |
| Local vector | cosine over the embedded chunks | `academy kb search "…" --vector`; study semantic vs lexical |
| **Azure hybrid** | BM25 + vector similarity, fused by the service | live mode; graceful fallback to local |

Try the teaching comparison:

```bash
academy kb search "time away when my mother is ill"            # keyword ranking
academy kb search "time away when my mother is ill" --vector   # vector ranking
```

Be precise about what you're seeing: the **mock** embedding is feature-hashed — a *soft
lexical* similarity, good for teaching the pipeline mechanics, not real semantics. It ranks by
shared vocabulary and chunk length, so its winner can differ from keyword's without being
smarter. True semantic wins ("mother is ill" → the caregiver policy even with zero shared
words) arrive when you switch to live `text-embedding-3-small` vectors — same command, env
vars set. That before/after is Lab 3.

## Azure AI Search setup

```bash
# .env
AZURE_SEARCH_ENDPOINT=https://<service>.search.windows.net
AZURE_SEARCH_KEY=<admin key>
AZURE_SEARCH_INDEX=hr-knowledge-base
# optional — real embeddings instead of the 256-dim mock:
AOAI_EMBED_DEPLOYMENT=text-embedding-3-small

academy kb push        # creates/updates the index, embeds and uploads every chunk
```

`azure_search.py` is plain REST on purpose — students see the wire contract: the index
definition (metadata filter fields + `content_vector` with an **HNSW vector profile** and a
semantic configuration), the `mergeOrUpload` batch, and the hybrid query with
`vectorQueries`. The index dimension always matches the active embedder, so mock-vector and
live-vector indexes both work.

Once pushed, set `ACADEMY_RUNTIME=live` and every scenario's CLASSIFY stage retrieves through
Azure AI Search hybrid — same chains, enterprise-grade retrieval.

## Labs

1. Add a policy document with correct frontmatter; `academy kb stats` must show it covering
   at least one scenario, and the whole suite must stay green.
2. Find a query where local keyword and local vector disagree on the top document. Explain
   which is right and why, in two sentences.
3. Provision a free-tier Azure AI Search service, `academy kb push`, and diff the hybrid
   results against local for the same three queries.
