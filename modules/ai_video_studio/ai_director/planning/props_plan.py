"""Props plan — lists props required per scene."""
from __future__ import annotations

from typing import Any


class PropsPlan:
    """Builds a props inventory."""

    def build(self, scenes: int = 1) -> dict[str, Any]:
        return {
            "props": [{"scene": i + 1, "items": ["script", "product", "water"]} for i in range(scenes)],
            "total_items": scenes * 3,
        }


_props_plan: PropsPlan | None = None


def get_props_plan() -> PropsPlan:
    global _props_plan
    if _props_plan is None:
        _props_plan = PropsPlan()
    return _props_plan
