"""Make-up plan — plans make-up and grooming needs."""
from __future__ import annotations

from typing import Any


class MakeUpPlan:
    """Defines make-up requirements per character."""

    def build(self, characters: list[str] | None = None) -> dict[str, Any]:
        names = characters or ["Host", "Guest"]
        return {name: {"base": "natural", "time_min": 15} for name in names}


_make_up_plan: MakeUpPlan | None = None


def get_make_up_plan() -> MakeUpPlan:
    global _make_up_plan
    if _make_up_plan is None:
        _make_up_plan = MakeUpPlan()
    return _make_up_plan
