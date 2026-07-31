from __future__ import annotations

import hashlib
import logging
import math

from ..knowledge_interfaces import EmbeddingProvider
from .tokenizer import Tokenizer


class HashEmbeddingGenerator(EmbeddingProvider):
    """Deterministic hashed n-gram embedding generator (no external models).

    Produces a sparse bag-of-hashed-ngrams vector that supports cosine
    similarity between semantically overlapping texts.
    """

    def __init__(self, dimensions: int = 384, ngram: int = 2) -> None:
        self._log = logging.getLogger("superdev.knowledge.embeddings.generator")
        self._dimensions = dimensions
        self._ngram = ngram
        self._tokenizer = Tokenizer()

    def embed(self, text: str) -> list[float]:
        tokens = self._tokenizer.tokenize(text)
        vector = [0.0] * self._dimensions
        if not tokens:
            return vector
        ngrams = self._ngrams(tokens)
        for gram in ngrams:
            digest = hashlib.sha256(gram.encode("utf-8")).digest()
            index = int.from_bytes(digest[:8], "big") % self._dimensions
            sign = 1.0 if digest[8] % 2 == 0 else -1.0
            vector[index] += sign
        norm = math.sqrt(sum(v * v for v in vector)) or 1.0
        return [v / norm for v in vector]

    def dimensions(self) -> int:
        return self._dimensions

    def _ngrams(self, tokens: list[str]) -> list[str]:
        if self._ngram <= 1 or len(tokens) < self._ngram:
            return tokens
        return [" ".join(tokens[i:i + self._ngram]) for i in range(len(tokens) - self._ngram + 1)]
