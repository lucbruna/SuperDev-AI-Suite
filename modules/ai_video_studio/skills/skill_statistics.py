"""Skill statistics — execution counters per skill."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass
class SkillUsage:
    calls: int = 0
    errors: int = 0
    total_ms: float = 0.0
    last_executed_at: str | None = None


class SkillStatistics:
    def __init__(self) -> None:
        self._usage: dict[str, SkillUsage] = {}

    def record(self, skill_id: str, *, ok: bool = True, duration_ms: float = 0.0) -> None:
        usage = self._usage.setdefault(skill_id, SkillUsage())
        usage.calls += 1
        if not ok:
            usage.errors += 1
        usage.total_ms += duration_ms
        usage.last_executed_at = datetime.now(UTC).isoformat()

    def stats(self) -> dict[str, Any]:
        return {
            "skills": {
                skill_id: {
                    "calls": u.calls,
                    "errors": u.errors,
                    "total_ms": round(u.total_ms, 3),
                    "last_executed_at": u.last_executed_at,
                }
                for skill_id, u in sorted(self._usage.items())
            },
            "total_calls": sum(u.calls for u in self._usage.values()),
            "total_errors": sum(u.errors for u in self._usage.values()),
            "reported_at": datetime.now(UTC).isoformat(),
        }


_statistics: SkillStatistics | None = None


def get_skill_statistics() -> SkillStatistics:
    global _statistics
    if _statistics is None:
        _statistics = SkillStatistics()
    return _statistics
