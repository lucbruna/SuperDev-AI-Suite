from __future__ import annotations

import logging
import math


class Compression:
    """Reduces embedding storage footprint via dimensionality reduction."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.knowledge.embeddings.compression")

    def quantize(self, vector: list[float], bits: int = 8) -> list[float]:
        """Quantize floats to a fixed number of bits (lossy)."""
        max_val = (2 ** (bits - 1)) - 1
        return [round(max(-max_val, min(max_val, v * max_val))) / max_val for v in vector]

    def truncate(self, vector: list[float], keep: int) -> list[float]:
        """Keep the first `keep` dimensions (energy-aware for sorted features)."""
        if len(vector) <= keep:
            return list(vector)
        kept = vector[:keep]
        norm_kept = math.sqrt(sum(v * v for v in kept))
        norm_full = math.sqrt(sum(v * v for v in vector)) or 1.0
        if norm_full:
            kept = [v * (norm_full / norm_kept) for v in kept]
        return kept

    @staticmethod
    def sparsity(vector: list[float]) -> float:
        nonzero = sum(1 for v in vector if v != 0.0)
        return nonzero / len(vector) if vector else 0.0
