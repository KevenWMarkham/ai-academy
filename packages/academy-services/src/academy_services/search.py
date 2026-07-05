"""Grounded retrieval over the HR policy knowledge base.

Mock mode is a transparent local keyword index over ``data/policies/*.md`` —
students can see exactly why a document ranked. Live mode is Azure AI Search
(hybrid/semantic) when ``AZURE_SEARCH_ENDPOINT``/``KEY`` are set and the
``azure-search-documents`` SDK is installed; otherwise it degrades to mock.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

_STOPWORDS = frozenset(
    "a an and are be can cannot do does for from how i in into is it many may me my next of on "
    "or should that the this to und was we what when where which who will with you your".split()
)


@dataclass(frozen=True)
class SearchHit:
    doc_id: str
    title: str
    score: float  # 0..1 — fraction of query terms matched (title terms weighted)
    snippet: str
    path: str


def _tokens(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-zà-ÿ]+", text.lower()) if t not in _STOPWORDS]


class PolicySearch:
    def __init__(self, data_dir: Path, runtime: str) -> None:
        self.runtime = runtime
        self._docs: list[tuple[str, str, str, Path]] = []  # (doc_id, title, body, path)
        for path in sorted((data_dir / "policies").glob("*.md")):
            body = path.read_text(encoding="utf-8")
            first_line = body.splitlines()[0].lstrip("# ").strip() if body else path.stem
            self._docs.append((path.stem, first_line, body, path))

    @property
    def live(self) -> bool:
        return (
            self.runtime in ("live", "maf")
            and bool(os.getenv("AZURE_SEARCH_ENDPOINT") and os.getenv("AZURE_SEARCH_KEY"))
        )

    def query(self, text: str, top: int = 3) -> list[SearchHit]:
        if self.live:
            try:
                return self._query_azure(text, top)
            except Exception:
                pass  # degrade gracefully to the local index
        return self._query_local(text, top)

    def _query_local(self, text: str, top: int) -> list[SearchHit]:
        query_terms = set(_tokens(text))
        if not query_terms:
            return []
        hits: list[SearchHit] = []
        for doc_id, title, body, path in self._docs:
            body_terms = set(_tokens(body))
            title_terms = set(_tokens(title))
            matched = query_terms & body_terms
            if not matched:
                continue
            score = len(matched) / len(query_terms)
            score += 0.15 * len(query_terms & title_terms)  # title matches rank higher
            hits.append(
                SearchHit(doc_id, title, round(min(score, 1.0), 2),
                          self._snippet(body, matched), str(path))
            )
        return sorted(hits, key=lambda h: h.score, reverse=True)[:top]

    @staticmethod
    def _snippet(body: str, matched: set[str]) -> str:
        """The paragraph containing the most matched terms — the citation the answer quotes."""
        best, best_hits = "", 0
        for para in (p.strip() for p in body.split("\n\n")):
            if not para or para.startswith("#"):
                continue
            hits = sum(1 for t in matched if t in para.lower())
            if hits > best_hits:
                best, best_hits = para, hits
        return best[:400]

    def _query_azure(self, text: str, top: int) -> list[SearchHit]:
        from azure.core.credentials import AzureKeyCredential
        from azure.search.documents import SearchClient

        client = SearchClient(
            endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
            index_name=os.getenv("AZURE_SEARCH_INDEX", "hr-policies"),
            credential=AzureKeyCredential(os.environ["AZURE_SEARCH_KEY"]),
        )
        results = client.search(text, top=top)
        return [
            SearchHit(
                doc_id=r.get("id", ""), title=r.get("title", ""),
                score=min(float(r.get("@search.score", 0.0)) / 10.0, 1.0),
                snippet=r.get("content", "")[:400], path=r.get("path", ""),
            )
            for r in results
        ]
