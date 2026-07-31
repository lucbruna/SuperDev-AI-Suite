"""Log processor."""
from __future__ import annotations
from typing import Any, Callable, Dict, List, Optional

class LogProcessor:
    def __init__(self) -> None:
        self._filters: List[Callable[[Dict[str, Any]], bool]] = []
        self._transformers: List[Callable[[Dict[str, Any]], Dict[str, Any]]] = []
    def add_filter(self, func: Callable[[Dict[str, Any]], bool]) -> None:
        self._filters.append(func)
    def add_transformer(self, func: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        self._transformers.append(func)
    def process(self, entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        for f in self._filters:
            if not f(entry):
                return None
        result = entry
        for t in self._transformers:
            result = t(result)
        return result
    def process_batch(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
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
