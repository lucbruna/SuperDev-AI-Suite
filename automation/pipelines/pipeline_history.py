"""History of pipeline runs."""

from __future__ import annotations

from typing import Any


class PipelineHistory:
    """Append-only log of pipeline executions."""

    def __init__(self) -> None:
        self._runs: list[dict[str, Any]] = []

    def record(self, run: Any) -> None:
        self._runs.append(run.to_dict())

    def list(self, limit: int = 50) -> list[dict[str, Any]]:
        return list(self._runs[-limit:])

    def count(self, status: str | None = None) -> int:
        if status is None:
            return len(self._runs)
        return sum(1 for r in self._runs if r["status"] == status)

    def clear(self) -> None:
        self._runs.clear()
