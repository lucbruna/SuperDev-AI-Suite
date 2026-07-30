from __future__ import annotations

from typing import Any


class LogAnalysis:
    """Analyzes log entries."""

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []

    def ingest_entry(self, entry: dict[str, Any]) -> str:
        self._entries.append(entry)
        return entry.get("id", str(len(self._entries) - 1))

    def search(self, query: str) -> list[dict[str, Any]]:
        return [e for e in self._entries if query.lower() in str(e.get("message", "")).lower()]

    @property
    def entry_count(self) -> int:
        return len(self._entries)

    def get_stats(self) -> dict[str, int]:
        return {"total": self.entry_count}

    def to_dict(self) -> dict[str, Any]:
        return {
            "entries": self._entries,
            "entry_count": self.entry_count,
        }
