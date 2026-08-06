"""Embedders — text → fixed-dimension vector.

The default :class:`HashEmbedder` is dependency-free and deterministic
(feature-hashing over token counts, md5-stable across processes), which keeps
the whole pipeline testable and offline. Real model embedders (e.g. an LLM
embedding API) can implement the same ``Embedder`` protocol and be swapped in
via config.
"""
from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol

_TOKEN_RE = re.compile(r"[a-z0-9_]+")


class Embedder(Protocol):
    """Protocol implemented by every embedder."""

    @property
    def dimensions(self) -> int: ...

    def embed(self, text: str) -> list[float]: ...


class HashEmbedder:
    """Deterministic bag-of-tokens embedder using feature hashing."""

    def __init__(self, dimensions: int = 256) -> None:
        if dimensions < 16:
            raise ValueError("dimensions must be >= 16")
        self._dimensions = dimensions

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed(self, text: str) -> list[float]:
        """Embed text into a normalized vector of ``dimensions`` floats."""
        vector = [0.0] * self._dimensions
        for token in _TOKEN_RE.findall(text.lower()):
            digest = hashlib.md5(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self._dimensions
            sign = 1.0 if digest[4] & 1 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]
