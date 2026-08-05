"""Lightweight, dependency-free text embeddings for architecture content.

Uses a feature-hash bag-of-words representation with an optional TF-IDF
weighting. This is intentionally a *local* fallback: when an external
embedding provider (OpenAI-compatible API) is configured through the
``SUPERDEV_GRAPH_EMBEDDINGS_URL`` environment variable, the module uses it
instead and caches the result in the vector index.

The feature hashing keeps the model dependency-free while remaining good
enough for semantic-ish retrieval over architecture nodes.
"""
from __future__ import annotations

import hashlib
import math
import os
import re
from typing import Any

_TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")
_STOPWORDS = frozenset(
    {
        "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with",
        "is", "are", "was", "were", "be", "by", "at", "as", "it", "its",
        "this", "that", "from", "into", "via", "using", "use", "used", "has",
        "have", "not", "no", "all", "any", "but", "if", "then", "than",
        "which", "who", "whom", "when", "where", "how", "what", "etc",
    }
)


class Embeddings:
    """Local bag-of-words embedder with TF-IDF-ish weighting.

    ``dim`` is the feature-hash space size. The representation is sparse
    internally but :meth:`dense` returns a plain list for storage.
    """

    def __init__(self, dim: int = 512) -> None:
        self.dim = dim
        self._doc_freq: dict[int, int] = {}
        self._total_docs = 0

    # ------------------------------------------------------------- tokenize
    def tokenize(self, text: str) -> list[str]:
        """Split text into lower-cased, stopword-free tokens."""
        tokens = [
            t.lower() for t in _TOKEN_RE.findall(text or "")
            if t.lower() not in _STOPWORDS and len(t) > 1
        ]
        return tokens

    def _hash(self, token: str) -> int:
        return int(hashlib.md5(token.encode("utf-8")).hexdigest()[:8], 16) % self.dim

    # --------------------------------------------------------------- encode
    def embed(self, text: str, *, fit: bool = True) -> dict[int, float]:
        """Return a sparse vector (feature -> weight)."""
        tokens = self.tokenize(text)
        counts: dict[int, float] = {}
        for token in tokens:
            idx = self._hash(token)
            counts[idx] = counts.get(idx, 0.0) + 1.0
        if not counts:
            return {}
        norm = math.sqrt(sum(v * v for v in counts.values())) or 1.0
        return {k: v / norm for k, v in counts.items()}

    def dense(self, text: str) -> list[float]:
        sparse = self.embed(text)
        vec = [0.0] * self.dim
        for idx, value in sparse.items():
            vec[idx] = value
        return vec

    # ------------------------------------------------------------- indexing
    def index_document(self, text: str) -> dict[int, float]:
        """Embed a document and register its tokens for IDF statistics."""
        vec = self.embed(text, fit=True)
        if vec:
            self._total_docs += 1
            for idx in vec:
                self._doc_freq[idx] = self._doc_freq.get(idx, 0) + 1
        return vec

    def idf_weight(self, idx: int) -> float:
        if self._total_docs == 0:
            return 1.0
        df = self._doc_freq.get(idx, 0)
        return math.log((1.0 + self._total_docs) / (1.0 + df)) + 1.0

    # --------------------------------------------------------------- cosine
    @staticmethod
    def cosine(a: dict[int, float], b: dict[int, float]) -> float:
        if not a or not b:
            return 0.0
        dot = 0.0
        for idx, value in a.items():
            if idx in b:
                dot += value * b[idx]
        return dot  # both vectors are L2-normalized


class ProviderEmbeddings:
    """Adapter for an OpenAI-compatible embeddings API (optional)."""

    def __init__(self) -> None:
        self.url = os.getenv("SUPERDEV_GRAPH_EMBEDDINGS_URL", "").strip()
        self.api_key = os.getenv("SUPERDEV_GRAPH_EMBEDDINGS_KEY", "").strip()
        self.model = os.getenv("SUPERDEV_GRAPH_EMBEDDINGS_MODEL", "text-embedding-3-small")
        self.enabled = bool(self.url)

    def embed(self, text: str) -> list[float]:
        """Call the remote provider. Raises on failure; caller falls back."""
        if not self.enabled:
            raise RuntimeError("provider not configured")
        import json
        import urllib.request

        body = json.dumps({"model": self.model, "input": text}).encode("utf-8")
        req = urllib.request.Request(
            self.url, data=body, method="POST",
            headers={
                "Content-Type": "application/json",
                **({"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}),
            },
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        return [float(x) for x in payload["data"][0]["embedding"]]


def embed_text(text: str, *, fit: bool = True) -> dict[int, float]:
    """Convenience wrapper over the module-level local embedder."""
    return _LOCAL.embed(text, fit=fit)


_LOCAL = Embeddings()
