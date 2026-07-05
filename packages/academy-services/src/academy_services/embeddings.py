"""Embeddings — the vector column of the knowledge base.

Live mode calls Azure OpenAI (``AOAI_EMBED_DEPLOYMENT``, e.g.
text-embedding-3-small → 1536 dims). Mock mode is a deterministic
feature-hashing embedder (256 dims, L2-normalized): every token hashes to a
signed slot, so cosine similarity still reflects lexical overlap. Students get
a real, working vector-search pipeline with zero credentials — and the same
code path upgrades to semantic vectors by setting env vars.
"""

from __future__ import annotations

import json
import math
import os
import re
import urllib.request
import zlib

from academy_services.foundry import aoai_ready

MOCK_DIMENSIONS = 256
LIVE_DIMENSIONS = 1536  # text-embedding-3-small

_TOKEN_RE = re.compile(r"[a-zà-ÿ0-9]+")


class EmbeddingService:
    def __init__(self, runtime: str) -> None:
        self.runtime = runtime

    @property
    def live(self) -> bool:
        return (
            self.runtime in ("live", "maf")
            and aoai_ready()
            and bool(os.getenv("AOAI_EMBED_DEPLOYMENT"))
        )

    @property
    def dimensions(self) -> int:
        return LIVE_DIMENSIONS if self.live else MOCK_DIMENSIONS

    def embed(self, text: str) -> list[float]:
        if self.live:
            try:
                return self._embed_aoai(text)
            except Exception:
                pass  # degrade gracefully — the mock vector keeps the pipeline alive
        return self.embed_mock(text)

    @staticmethod
    def embed_mock(text: str) -> list[float]:
        """Deterministic feature-hashing embedding: token → signed slot, then L2-normalize."""
        vector = [0.0] * MOCK_DIMENSIONS
        for token in _TOKEN_RE.findall(text.lower()):
            digest = zlib.crc32(token.encode("utf-8"))
            slot = digest % MOCK_DIMENSIONS
            sign = 1.0 if (digest >> 9) & 1 else -1.0
            vector[slot] += sign
        norm = math.sqrt(sum(v * v for v in vector))
        return [v / norm for v in vector] if norm else vector

    @staticmethod
    def _embed_aoai(text: str) -> list[float]:
        endpoint = os.environ["AOAI_ENDPOINT"].rstrip("/")
        deployment = os.environ["AOAI_EMBED_DEPLOYMENT"]
        version = os.getenv("AOAI_API_VERSION", "2024-10-21")
        url = f"{endpoint}/openai/deployments/{deployment}/embeddings?api-version={version}"
        request = urllib.request.Request(
            url,
            data=json.dumps({"input": text}).encode("utf-8"),
            headers={
                "api-key": os.getenv("AOAI_KEY") or os.environ["AOAI_API_KEY"],
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
        return list(payload["data"][0]["embedding"])


def cosine(a: list[float], b: list[float]) -> float:
    """Cosine similarity for already-normalized vectors (falls back to full formula)."""
    dot = sum(x * y for x, y in zip(a, b, strict=True))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0
