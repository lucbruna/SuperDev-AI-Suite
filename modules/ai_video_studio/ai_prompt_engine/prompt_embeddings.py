"""Prompt embeddings — local feature-based prompt similarity vectors."""
from __future__ import annotations

import hashlib
import re
from typing import Any

STOPWORDS = {
    "de", "da", "do", "dos", "das", "e", "ou", "um", "uma", "para", "com", "sobre",
    "em", "no", "na", "por", "que", "the", "a", "an", "of", "and", "for", "with",
}


class PromptEmbeddings:
    """Deterministic bag-of-tokens embeddings (no external model)."""

    def vectorize(self, prompt: str) -> dict[str, int]:
        tokens = re.findall(r"[a-zà-ú0-9]+", (prompt or "").lower())
        vector: dict[str, int] = {}
        for t in tokens:
            if t in STOPWORDS:
                continue
            vector[t] = vector.get(t, 0) + 1
        return vector

    def similarity(self, a: str, b: str) -> float:
        """Cosine similarity between two prompt vectors (0..1)."""
        va, vb = self.vectorize(a), self.vectorize(b)
        if not va or not vb:
            return 0.0
        common = set(va) & set(vb)
        dot = sum(va[t] * vb[t] for t in common)
        na = sum(v * v for v in va.values()) ** 0.5
        nb = sum(v * v for v in vb.values()) ** 0.5
        if na == 0 or nb == 0:
            return 0.0
        return round(dot / (na * nb), 4)

    def digest(self, prompt: str) -> str:
        """Stable hash fingerprint for prompt dedup."""
        return hashlib.sha256((prompt or "").strip().lower().encode("utf-8")).hexdigest()[:16]

    def nearest(self, prompt: str, candidates: list[str], top_k: int = 3) -> list[dict[str, Any]]:
        scored = [{"prompt": c, "similarity": self.similarity(prompt, c)} for c in candidates]
        scored.sort(key=lambda x: x["similarity"], reverse=True)
        return scored[:top_k]


_prompt_embeddings: PromptEmbeddings | None = None


def get_prompt_embeddings() -> PromptEmbeddings:
    global _prompt_embeddings
    if _prompt_embeddings is None:
        _prompt_embeddings = PromptEmbeddings()
    return _prompt_embeddings
