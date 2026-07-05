"""The HR knowledge base — a governed markdown corpus, chunked into search records.

Every document under ``data/kb/`` carries frontmatter metadata: what kind of
document it is, which jurisdictions and language it covers, and — crucially —
which scenarios it grounds (``scenarios: [hr-hrsd-01, …]``). The chunker splits
each document at its ``##`` sections; each chunk becomes one search record that
can carry a ``content_vector`` embedding (see :mod:`academy_services.embeddings`
and ``academy kb build --vectors``).
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from academy_services.embeddings import EmbeddingService

_LIST_FIELDS = frozenset({"jurisdictions", "scenarios", "tags"})


def parse_front_matter(raw: str) -> tuple[dict[str, object], str]:
    """Parse the ``---`` frontmatter block (a deliberate yaml-lite: no dependency)."""
    if not raw.startswith("---"):
        return {}, raw
    parts = raw.split("---", 2)
    if len(parts) < 3:
        return {}, raw
    meta: dict[str, object] = {}
    for line in parts[1].strip().splitlines():
        key, sep, value = line.partition(":")
        if not sep:
            continue
        key, value = key.strip(), value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1]
        if key in _LIST_FIELDS:
            meta[key] = tuple(v.strip() for v in value.strip("[]").split(",") if v.strip())
        else:
            meta[key] = value
    return meta, parts[2].lstrip("\n")


@dataclass(frozen=True)
class KbChunk:
    """One search record — the unit that gets embedded and indexed."""

    id: str  # "<doc_id>-<nn>", the Azure AI Search document key
    doc_id: str
    title: str
    section: str
    content: str
    doc_type: str
    category: str
    language: str
    jurisdictions: tuple[str, ...]
    scenarios: tuple[str, ...]
    tags: tuple[str, ...]
    path: str

    def to_record(self, vector: list[float] | None = None) -> dict[str, object]:
        record: dict[str, object] = asdict(self)
        record["jurisdictions"] = list(self.jurisdictions)
        record["scenarios"] = list(self.scenarios)
        record["tags"] = list(self.tags)
        if vector is not None:
            record["content_vector"] = vector
        return record


def _split_sections(body: str) -> list[tuple[str, str]]:
    """Split a markdown body at ``##`` headings; the preamble becomes 'Overview'."""
    sections: list[tuple[str, str]] = []
    heading, lines = "Overview", []

    def flush() -> None:
        text = "\n".join(lines).strip()
        if text:
            sections.append((heading, text))

    for line in body.splitlines():
        if line.startswith("## "):
            flush()
            heading, lines = line[3:].strip(), []
        elif line.startswith("# "):
            continue  # the document title lives in frontmatter
        else:
            lines.append(line)
    flush()
    return sections


class KnowledgeBase:
    """Loads ``data/kb/**/*.md`` into chunks with metadata."""

    def __init__(self, data_dir: Path) -> None:
        self.root = data_dir / "kb"
        self.chunks: list[KbChunk] = []
        self.documents: dict[str, dict[str, object]] = {}
        for path in sorted(self.root.rglob("*.md")):
            meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
            doc_id = path.stem
            title = str(meta.get("title") or doc_id)
            self.documents[doc_id] = {**meta, "title": title, "path": str(path)}
            for i, (section, content) in enumerate(_split_sections(body)):
                self.chunks.append(
                    KbChunk(
                        id=f"{doc_id}-{i:02d}",
                        doc_id=doc_id,
                        title=title,
                        section=section,
                        content=content,
                        doc_type=str(meta.get("doc_type", "article")),
                        category=str(meta.get("category", path.parent.name)),
                        language=str(meta.get("language", "en")),
                        jurisdictions=tuple(meta.get("jurisdictions", ()) or ()),  # type: ignore[arg-type]
                        scenarios=tuple(meta.get("scenarios", ()) or ()),  # type: ignore[arg-type]
                        tags=tuple(meta.get("tags", ()) or ()),  # type: ignore[arg-type]
                        path=str(path),
                    )
                )

    def scenario_coverage(self) -> dict[str, list[str]]:
        """scenario id → the documents that ground it (the KB's teaching contract)."""
        coverage: dict[str, list[str]] = {}
        for doc_id, meta in self.documents.items():
            for scenario_id in meta.get("scenarios", ()) or ():  # type: ignore[union-attr]
                coverage.setdefault(str(scenario_id), []).append(doc_id)
        return {k: sorted(v) for k, v in sorted(coverage.items())}

    def build_jsonl(
        self,
        out_path: Path,
        embedder: EmbeddingService | None = None,
    ) -> Path:
        """Write one JSON record per chunk; with an embedder, each record carries
        its ``content_vector`` — the embedded vector search column."""
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as fh:
            for chunk in self.chunks:
                vector = (
                    embedder.embed(f"{chunk.title} · {chunk.section}\n{chunk.content}")
                    if embedder
                    else None
                )
                fh.write(json.dumps(chunk.to_record(vector), ensure_ascii=False) + "\n")
        return out_path
