"""Azure AI Search integration — index provisioning, upload, and hybrid queries.

Deliberately plain REST (urllib, no SDK) so students can read the exact wire
contract: the index definition with its vector field + HNSW profile, the
document batch upload, and the hybrid (text + vector) query. Configure with::

    AZURE_SEARCH_ENDPOINT=https://<service>.search.windows.net
    AZURE_SEARCH_KEY=<admin key for push, query key for search>
    AZURE_SEARCH_INDEX=hr-knowledge-base
"""

from __future__ import annotations

import json
import os
import urllib.request
from typing import Any

from academy_services.embeddings import EmbeddingService
from academy_services.kb import KbChunk

API_VERSION = "2024-07-01"


def search_configured() -> bool:
    return bool(os.getenv("AZURE_SEARCH_ENDPOINT") and os.getenv("AZURE_SEARCH_KEY"))


def index_name() -> str:
    return os.getenv("AZURE_SEARCH_INDEX", "hr-knowledge-base")


def index_definition(name: str, vector_dimensions: int) -> dict[str, Any]:
    """The index schema: metadata filters + full-text content + the vector column."""
    string_field = {"type": "Edm.String", "filterable": True, "facetable": True}
    collection = {"type": "Collection(Edm.String)", "filterable": True, "facetable": True}
    return {
        "name": name,
        "fields": [
            {"name": "id", "type": "Edm.String", "key": True, "filterable": True},
            {"name": "doc_id", **string_field},
            {"name": "title", "type": "Edm.String", "searchable": True},
            {"name": "section", "type": "Edm.String", "searchable": True},
            {"name": "content", "type": "Edm.String", "searchable": True},
            {"name": "doc_type", **string_field},
            {"name": "category", **string_field},
            {"name": "language", **string_field},
            {"name": "jurisdictions", **collection},
            {"name": "scenarios", **collection},
            {"name": "tags", **collection},
            {"name": "path", "type": "Edm.String"},
            {
                "name": "content_vector",
                "type": "Collection(Edm.Single)",
                "searchable": True,
                "retrievable": False,
                "dimensions": vector_dimensions,
                "vectorSearchProfile": "kb-vector-profile",
            },
        ],
        "vectorSearch": {
            "algorithms": [{"name": "kb-hnsw", "kind": "hnsw"}],
            "profiles": [{"name": "kb-vector-profile", "algorithm": "kb-hnsw"}],
        },
        "semantic": {
            "configurations": [
                {
                    "name": "kb-semantic",
                    "prioritizedFields": {
                        "titleField": {"fieldName": "title"},
                        "prioritizedContentFields": [{"fieldName": "content"}],
                        "prioritizedKeywordsFields": [{"fieldName": "section"}],
                    },
                }
            ]
        },
    }


def _call(method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    endpoint = os.environ["AZURE_SEARCH_ENDPOINT"].rstrip("/")
    request = urllib.request.Request(
        f"{endpoint}{path}?api-version={API_VERSION}",
        method=method,
        data=json.dumps(payload).encode("utf-8") if payload is not None else None,
        headers={
            "api-key": os.environ["AZURE_SEARCH_KEY"],
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        body = response.read().decode("utf-8")
    return json.loads(body) if body else {}


def ensure_index(vector_dimensions: int) -> str:
    """Create or update the index (PUT is idempotent for compatible changes)."""
    name = index_name()
    _call("PUT", f"/indexes/{name}", index_definition(name, vector_dimensions))
    return name


def upload_chunks(
    chunks: list[KbChunk], embedder: EmbeddingService, batch_size: int = 100
) -> int:
    """Embed and upload every chunk; returns the number of documents indexed."""
    name = index_name()
    uploaded = 0
    for start in range(0, len(chunks), batch_size):
        batch = chunks[start : start + batch_size]
        actions = []
        for chunk in batch:
            record = chunk.to_record(
                embedder.embed(f"{chunk.title} · {chunk.section}\n{chunk.content}")
            )
            actions.append({"@search.action": "mergeOrUpload", **record})
        _call("POST", f"/indexes/{name}/docs/index", {"value": actions})
        uploaded += len(batch)
    return uploaded


def hybrid_query(
    text: str, embedder: EmbeddingService, top: int = 3, language: str = "en"
) -> list[dict[str, Any]]:
    """Hybrid retrieval: BM25 full-text + vector similarity, fused by the service."""
    payload = {
        "search": text,
        "top": top,
        "filter": f"language eq '{language}'",
        "select": "id,doc_id,title,section,content,category,scenarios,path",
        "vectorQueries": [
            {
                "kind": "vector",
                "vector": embedder.embed(text),
                "fields": "content_vector",
                "k": top,
            }
        ],
    }
    result = _call("POST", f"/indexes/{index_name()}/docs/search", payload)
    return list(result.get("value", []))
