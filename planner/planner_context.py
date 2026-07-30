from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class PlannerContext:
    """Context for plan creation and execution."""

    def __init__(self):
        self._data: dict[str, Any] = {}
        self._history: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> PlannerContext:
        ctx = PlannerContext()
        ctx._data = kwargs
        ctx._record("created")
        return ctx

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self._record(f"set:{key}")

    def update(self, data: dict[str, Any]) -> None:
        self._data.update(data)
        self._record("updated")

    def snapshot(self) -> dict[str, Any]:
        return dict(self._data)

    def clear(self) -> None:
        self._data.clear()
        self._record("cleared")

    def _record(self, action: str) -> None:
        self._history.append({
            "action": action,
            "timestamp": datetime.now(UTC).isoformat(),
        })
