"""AIOS Perception — structured interpretation of raw input.

Turns arbitrary input into a list of typed percepts (observations)
with confidence, so downstream cognition works on uniform data.
"""

from __future__ import annotations

from typing import Any


class Perception:
    """Interpret raw input into structured percepts."""

    def interpret(self, raw: Any) -> list[dict[str, Any]]:
        if isinstance(raw, dict):
            return [
                {"type": "field", "key": str(key), "value": value, "confidence": 1.0}
                for key, value in raw.items()
            ]
        if isinstance(raw, (list, tuple, set)):
            return [
                {"type": "element", "key": str(index), "value": value, "confidence": 1.0}
                for index, value in enumerate(raw)
            ]
        return [{"type": "value", "key": "raw", "value": raw, "confidence": 1.0}]

    def normalize(self, raw: Any) -> dict[str, Any]:
        """Flatten a mapping to string keys (nested dicts kept as-is)."""
        if not isinstance(raw, dict):
            return {"value": raw}
        return {str(key): value for key, value in raw.items()}
