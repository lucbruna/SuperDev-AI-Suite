from __future__ import annotations

from typing import Any


class VectorCompression:
    """Compress and decompress vector representations."""

    @staticmethod
    def compress(vector: list[float], bits: int = 8) -> list[int]:
        """Quantize float vector to integer representation."""
        if not vector:
            return []
        max_val = max(abs(v) for v in vector)
        if max_val == 0:
            return [0] * len(vector)
        scale = (1 << (bits - 1)) - 1
        return [int(round(v / max_val * scale)) for v in vector]

    @staticmethod
    def decompress(compressed: list[int], original_magnitude: float = 1.0) -> list[float]:
        """Dequantize integer representation back to floats."""
        if not compressed:
            return []
        bits = 8  # default
        scale = (1 << (bits - 1)) - 1
        return [float(c) / scale * original_magnitude for c in compressed]

    @staticmethod
    def ratio(original: list[float], compressed: list[int]) -> float:
        """Calculate compression ratio (compressed / original bytes)."""
        orig_bytes = len(original) * 4  # float32
        comp_bytes = len(compressed) * 2  # int16
        return comp_bytes / orig_bytes if orig_bytes else 1.0
