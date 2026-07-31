from __future__ import annotations

from collections.abc import Callable
from typing import Any


class ModelUpdater:
    """Updates internal models with new data."""

    def __init__(self):
        self._version: int = 0
        self._update_log: list[dict[str, Any]] = []

    @property
    def version(self) -> int:
        return self._version

    @property
    def update_count(self) -> int:
        return len(self._update_log)

    def update(self, data: list[dict[str, Any]], strategy: str = "replace") -> int:
        self._version += 1
        entry: dict[str, Any] = {
            "version": self._version,
            "strategy": strategy,
            "sample_count": len(data),
        }
        self._update_log.append(entry)
        return self._version

    def apply_update(self, updater_fn: Callable) -> Any:
        result = updater_fn()
        self._version += 1
        self._update_log.append({"version": self._version, "custom": True})
        return result

    def rollback(self, target_version: int) -> bool:
        if target_version < 1 or target_version >= self._version:
            return False
        self._version = target_version
        self._update_log = [e for e in self._update_log if e["version"] <= target_version]
        return True

    def clear(self) -> None:
        self._version = 0
        self._update_log.clear()
