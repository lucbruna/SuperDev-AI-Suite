from __future__ import annotations

import asyncio
import json
import os
from typing import Any

from ..base.base_memory import BaseMemory


class LongTermMemory(BaseMemory):
    def __init__(self, storage_path: str | None = None) -> None:
        self._storage_path = storage_path or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "..", "memory_store"
        )
        os.makedirs(self._storage_path, exist_ok=True)
        self._data: dict[str, Any] = {}
        self._lock = asyncio.Lock()
        self._load_all()

    def _load_all(self) -> None:
        if not os.path.isdir(self._storage_path):
            return
        for fname in os.listdir(self._storage_path):
            if fname.endswith(".json"):
                key = fname[:-5]
                try:
                    with open(os.path.join(self._storage_path, fname), encoding="utf-8") as f:
                        self._data[key] = json.load(f)
                except Exception:
                    pass

    async def store(self, key: str, value: Any) -> None:
        async with self._lock:
            self._data[key] = value
            filepath = os.path.join(self._storage_path, f"{key}.json")
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(value, f, indent=2, default=str)

    async def retrieve(self, key: str) -> Any | None:
        async with self._lock:
            return self._data.get(key)

    async def search(self, query: str) -> list[Any]:
        results = []
        q = query.lower()
        async with self._lock:
            for key, value in self._data.items():
                if q in key.lower():
                    results.append(value)
        return results

    async def delete(self, key: str) -> None:
        async with self._lock:
            self._data.pop(key, None)
            filepath = os.path.join(self._storage_path, f"{key}.json")
            if os.path.exists(filepath):
                os.remove(filepath)

    async def clear(self) -> None:
        async with self._lock:
            self._data.clear()
            for fname in os.listdir(self._storage_path):
                if fname.endswith(".json"):
                    os.remove(os.path.join(self._storage_path, fname))

    async def summarize(self) -> str:
        async with self._lock:
            keys = list(self._data.keys())
            return f"LongTermMemory: {len(keys)} entries. Keys: {', '.join(keys[:20])}"
