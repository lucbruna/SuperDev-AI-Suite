"""Diagnostics history."""

from __future__ import annotations

import time
from typing import Any


class DiagnosticsHistory:
    def __init__(self, max_entries: int = 500) -> None:
        self._entries: list[dict[str, Any]] = []
        self._max = max_entries

    def record(self, diagnosis: dict[str, Any]) -> dict[str, Any]:
        entry = {"diagnosis": diagnosis, "timestamp": time.time()}
        self._entries.append(entry)
        if len(self._entries) > self._max:
            self._entries = self._entries[-self._max :]
        return entry

    def query(self, problem: str = "", limit: int = 100) -> list[dict[str, Any]]:
        results = self._entries
        if problem:
            results = [e for e in results if problem.lower() in str(e.get("diagnosis", {})).lower()]
        return results[-limit:]

    def count(self) -> int:
        return len(self._entries)

    def clear(self) -> int:
        n = len(self._entries)
        self._entries.clear()
        return n

    def get_recent(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._entries[-limit:]
