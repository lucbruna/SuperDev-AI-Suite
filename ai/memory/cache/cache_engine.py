from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .cache_store import CacheStore


class CacheEngine:
    """Central cache orchestrator."""

    def __init__(self, default_ttl: float = 300.0, max_size: int = 1000) -> None:
        self._default_ttl = default_ttl
        self._max_size = max_size
        self._stores: dict[str, CacheStore] = {}

    @property
    def default_ttl(self) -> float:
        return self._default_ttl

    @property
    def max_size(self) -> int:
        return self._max_size

    @property
    def store_names(self) -> list[str]:
        return list(self._stores.keys())

    def register_store(self, name: str, store: CacheStore) -> None:
        self._stores[name] = store

    def get(self, key: str, store_name: str | None = None) -> Any | None:
        if store_name:
            store = self._stores.get(store_name)
            return store.get(key) if store else None
        for store in self._stores.values():
            value = store.get(key)
            if value is not None:
                return value
        return None

    def set(self, key: str, value: Any, ttl: float | None = None, store_name: str | None = None) -> None:
        ttl = ttl if ttl is not None else self._default_ttl
        if store_name:
            store = self._stores.get(store_name)
            if store:
                store.set(key, value, ttl)
        else:
            for store in self._stores.values():
                store.set(key, value, ttl)

    def delete(self, key: str, store_name: str | None = None) -> bool:
        if store_name:
            store = self._stores.get(store_name)
            return store.delete(key) if store else False
        removed = False
        for store in self._stores.values():
            if store.delete(key):
                removed = True
        return removed

    def clear(self, store_name: str | None = None) -> None:
        if store_name:
            store = self._stores.get(store_name)
            if store:
                store.clear()
        else:
            for store in self._stores.values():
                store.clear()

    def stats(self) -> dict[str, Any]:
        return {
            "stores": len(self._stores),
            "default_ttl": self._default_ttl,
            "max_size": self._max_size,
        }
