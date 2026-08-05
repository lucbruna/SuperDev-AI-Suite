"""Transition motion — blend between motion clips."""
from __future__ import annotations

from typing import Any


class TransitionMotion:
    """Blends two clips over a transition window."""

    def blend(self, clip_a: list[dict[str, Any]], clip_b: list[dict[str, Any]], *, window: int = 5) -> list[dict[str, Any]]:
        if not clip_a or not clip_b:
            raise ValueError("Both clips must be non-empty")
        result = list(clip_a)
        for i in range(1, window + 1):
            alpha = i / (window + 1)
            merged = dict(clip_a[-1])
            for key, value in clip_b[0].items():
                if isinstance(value, (int, float)) and isinstance(merged.get(key), (int, float)):
                    merged[key] = merged[key] + (value - merged[key]) * alpha
                else:
                    merged[key] = value
            result.append(merged)
        result.extend(clip_b)
        return result
