"""Dialect detector — identifies dialect / regional variants in the script."""
from __future__ import annotations

from typing import Any


class DialectDetector:
    """Detects common dialect markers in Portuguese scripts."""

    def detect(self, text: str) -> dict[str, Any]:
        lowered = text.lower()
        dialect = "neutral"
        if any(word in lowered for word in ("tu", "vocês viram", "maninho")):
            dialect = "pt-br_sul"
        elif any(word in lowered for word in ("oxe", "mainha", "tu é doido")):
            dialect = "pt-br_nordeste"
        elif any(word in lowered for word in ("fixe", "bué", "pá")):
            dialect = "pt-pt"
        return {"dialect": dialect, "markers_found": dialect != "neutral"}


_dialect_detector: DialectDetector | None = None


def get_dialect_detector() -> DialectDetector:
    global _dialect_detector
    if _dialect_detector is None:
        _dialect_detector = DialectDetector()
    return _dialect_detector
