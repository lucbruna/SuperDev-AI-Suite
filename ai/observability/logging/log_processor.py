"""Log processor."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any


class LogProcessor:
    def __init__(self) -> None:
        self._filters: list[Callable[[dict[str, Any]], bool]] = []
        self._transformers: list[Callable[[dict[str, Any]], dict[str, Any]]] = []
    def add_filter(self, func: Callable[[dict[str, Any]], bool]) -> None:
        self._filters.append(func)
    def add_transformer(self, func: Callable[[dict[str, Any]], dict[str, Any]]) -> None:
        self._transformers.append(func)
    def process(self, entry: dict[str, Any]) -> dict[str, Any] | None:
        for f in self._filters:
            if not f(entry):
                return None
        result = entry
        for t in self._transformers:
            result = t(result)
        return result
    def process_batch(self, entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
        results = []
        for e in entries:
            processed = self.process(e)
            if processed is not None:
                results.append(processed)
        return results
    def filter_count(self) -> int:
        return len(self._filters)
    def transformer_count(self) -> int:
        return len(self._transformers)
