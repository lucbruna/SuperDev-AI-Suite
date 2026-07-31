"""Dataset management."""
from __future__ import annotations

import time
from typing import Any


class DatasetManager:
    def __init__(self) -> None:
        self._datasets: dict[str, dict[str, Any]] = {}
    def create(self, name: str, entries: list[dict[str, Any]], format_type: str = "json") -> dict[str, Any]:
        ds = {"name": name, "entries": entries, "format": format_type, "created_at": time.time(), "size": len(entries)}
        self._datasets[name] = ds
        return {"name": name, "size": len(entries)}
    def get(self, name: str) -> dict[str, Any]:
        return self._datasets.get(name, {"error": "not_found"})
    def update(self, name: str, entries: list[dict[str, Any]]) -> bool:
        if name not in self._datasets:
            return False
        self._datasets[name]["entries"].extend(entries)
        self._datasets[name]["size"] = len(self._datasets[name]["entries"])
        return True
    def delete(self, name: str) -> bool:
        if name in self._datasets:
            del self._datasets[name]
            return True
        return False
    def filter_entries(self, name: str, filter_fn) -> list[dict[str, Any]]:
        ds = self._datasets.get(name, {})
        entries = ds.get("entries", [])
        return [e for e in entries if filter_fn(e)]
    def sample(self, name: str, count: int = 10) -> list[dict[str, Any]]:
        import random
        ds = self._datasets.get(name, {})
        entries = ds.get("entries", [])
        return random.sample(entries, min(count, len(entries)))
    def list_datasets(self) -> list[str]:
        return list(self._datasets.keys())
    def count(self, name: str) -> int:
        return len(self._datasets.get(name, {}).get("entries", []))
