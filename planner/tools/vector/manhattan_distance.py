from __future__ import annotations


class ManhattanDistance:
    """Manhattan distance computation."""

    @staticmethod
    def compute(a: list[float], b: list[float]) -> float:
        if len(a) != len(b) or not a:
            return float("inf")
        return sum(abs(x - y) for x, y in zip(a, b))
