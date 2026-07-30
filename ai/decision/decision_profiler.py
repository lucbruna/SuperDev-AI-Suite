from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class DecisionProfiler:
    """Profiler for decision-making performance."""

    def __init__(self):
        self._marks: dict[str, float] = {}

    def start(self, label: str = "root") -> None:
        self._marks[label] = datetime.now(timezone.utc).timestamp()

    def stop(self, label: str = "root") -> float:
        start = self._marks.pop(label, 0.0)
        if start == 0:
            return 0.0
        return (datetime.now(timezone.utc).timestamp() - start) * 1000

    def report(self) -> dict[str, Any]:
        return {"active_marks": list(self._marks.keys())}
