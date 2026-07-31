"""Log indexing and search (Volume 37, Fase 4)."""

from __future__ import annotations

from devops_engine.devops_models import LogEntry
from devops_engine.devops_protocols import tokenize


class LogIndex:
    """Token-based inverted index over log entries."""

    def __init__(self) -> None:
        self._index: dict[str, list[LogEntry]] = {}

    def index(self, entry: LogEntry) -> bool:
        for token in tokenize(f"{entry.source} {entry.message}"):
            self._index.setdefault(token, []).append(entry)
        return True

    def search(self, query: str, level: str | None = None,
               source: str | None = None,
               limit: int = 50) -> list[LogEntry]:
        tokens = tokenize(query)
        if not tokens:
            return []
        result = list(self._index.get(tokens[0], []))
        for token in tokens[1:]:
            result = [entry for entry in result
                      if entry in self._index.get(token, [])]
        if level:
            result = [entry for entry in result
                      if entry.level == level]
        if source:
            result = [entry for entry in result
                      if entry.source == source]
        return result[:max(0, limit)]

    def count(self) -> int:
        return len(self._index)
