"""Grounded retrieval over the HR knowledge base.

Local mode (default) is a transparent keyword index over the KB chunks —
students can see exactly why a document ranked — plus a local **vector** mode
(cosine over the mock embeddings) to study the difference. Live mode runs a
**hybrid text + vector** query against Azure AI Search when configured, and
degrades gracefully back to local.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from academy_services.embeddings import EmbeddingService, cosine
from academy_services.kb import KbChunk, KnowledgeBase

_STOPWORDS = frozenset(
    "a an and are be can cannot do does for from how i in into is it many may me my next of on "
    "or should that the this to und was we what when where which who will with you your".split()
)


@dataclass(frozen=True)
class SearchHit:
    doc_id: str
    title: str
    score: float  # 0..1 — keyword: fraction of query terms matched (title-weighted)
    snippet: str
    path: str
    section: str = ""


def _tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-zà-ÿ]+", text.lower()) if t not in _STOPWORDS]


class KBSearch:
    """The retrieval seat of the chain — always returns cited, scoped hits."""

    def __init__(self, data_dir: Path, runtime: str, embedder: EmbeddingService) -> None:
        self.runtime = runtime
        self.embedder = embedder
        self.kb = KnowledgeBase(data_dir)

    @property
    def live(self) -> bool:
        import os

        return (
            self.runtime in ("live", "maf")
            and bool(os.getenv("AZURE_SEARCH_ENDPOINT") and os.getenv("AZURE_SEARCH_KEY"))
        )

    def query(self, text: str, top: int = 3, language: str = "en") -> list[SearchHit]:
        """Best chunk per document — the citation the scenario quotes."""
        if self.live:
            try:
                return self._query_azure(text, top, language)
            except Exception:
                pass  # degrade gracefully to the local index
        return self._query_local(text, top, language)

    # ---- local keyword (deterministic, explainable) --------------------------

    def _query_local(self, text: str, top: int, language: str) -> list[SearchHit]:
        query_terms = set(_tokens(text))
        if not query_terms:
            return []
        best_per_doc: dict[str, SearchHit] = {}
        for chunk in self.kb.chunks:
            if chunk.language != language:
                continue
            matched = query_terms & set(_tokens(chunk.content))
            if not matched:
                continue
            score = len(matched) / len(query_terms)
            score += 0.15 * len(query_terms & set(_tokens(chunk.title)))
            hit = SearchHit(
                doc_id=chunk.doc_id,
                title=chunk.title,
                score=round(min(score, 1.0), 2),
                snippet=chunk.content[:400],
                path=chunk.path,
                section=chunk.section,
            )
            current = best_per_doc.get(chunk.doc_id)
            if current is None or hit.score > current.score:
                best_per_doc[chunk.doc_id] = hit
        return sorted(best_per_doc.values(), key=lambda h: h.score, reverse=True)[:top]

    # ---- local vector (cosine over the embedded chunks) ----------------------

    @cached_property
    def _chunk_vectors(self) -> list[tuple[KbChunk, list[float]]]:
        return [
            (c, self.embedder.embed(f"{c.title} · {c.section}\n{c.content}"))
            for c in self.kb.chunks
        ]

    def vector_query(self, text: str, top: int = 3, language: str = "en") -> list[SearchHit]:
        """Pure vector retrieval over the ``content_vector`` column (chunk-level)."""
        query_vector = self.embedder.embed(text)
        scored = [
            (cosine(query_vector, vector), chunk)
            for chunk, vector in self._chunk_vectors
            if chunk.language == language
        ]
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [
            SearchHit(
                doc_id=c.doc_id, title=c.title, score=round(max(s, 0.0), 3),
                snippet=c.content[:400], path=c.path, section=c.section,
            )
            for s, c in scored[:top]
        ]

    # ---- Azure AI Search (hybrid text + vector) -------------------------------

    def _query_azure(self, text: str, top: int, language: str) -> list[SearchHit]:
        from academy_services.azure_search import hybrid_query

        results = hybrid_query(text, self.embedder, top=top, language=language)
        return [
            SearchHit(
                doc_id=r.get("doc_id", ""),
                title=r.get("title", ""),
                score=min(round(float(r.get("@search.score", 0.0)) / 4.0, 2), 1.0),
                snippet=r.get("content", "")[:400],
                path=r.get("path", ""),
                section=r.get("section", ""),
            )
            for r in results
        ]


#: Backwards-compatible alias — the policy KB is now the full knowledge base.
PolicySearch = KBSearch
