"""Dataset management."""
from __future__ import annotations
from typing import Any, Dict, List
import time

class DatasetManager:
    def __init__(self) -> None:
        self._datasets: Dict[str, Dict[str, Any]] = {}
    def create(self, name: str, entries: List[Dict[str, Any]], format_type: str = "json") -> Dict[str, Any]:
        ds = {"name": name, "entries": entries, "format": format_type, "created_at": time.time(), "size": len(entries)}
        self._datasets[name] = ds
        return {"name": name, "size": len(entries)}
    def get(self, name: str) -> Dict[str, Any]:
        return self._datasets.get(name, {"error": "not_found"})
    def update(self, name: str, entries: List[Dict[str, Any]]) -> bool:
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
    def filter_entries(self, name: str, filter_fn) -> List[Dict[str, Any]]:
        ds = self._datasets.get(name, {})
        entries = ds.get("entries", [])
        return [e for e in entries if filter_fn(e)]
    def sample(self, name: str, count: int = 10) -> List[Dict[str, Any]]:
        import random
        ds = self._datasets.get(name, {})
        entries = ds.get("entries", [])
        return random.sample(entries, min(count, len(entries)))
    def list_datasets(self) -> List[str]:
        return list(self._datasets.keys())
    def count(self, name: str) -> int:
        return len(self._datasets.get(name, {}).get("entries", []))
