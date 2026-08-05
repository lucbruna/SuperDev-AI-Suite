"""Avatar cache — bounded LRU-style cache for generated artifacts."""
from __future__ import annotations

from collections import OrderedDict
from typing import Any


class AvatarCache:
    """Simple bounded cache (ordered-dict LRU) for avatar artifacts."""

    def __init__(self, capacity: int = 256) -> None:
        self.capacity = max(1, capacity)
        self._store: OrderedDict[str, Any] = OrderedDict()

    def get(self, key: str) -> Any | None:
        if key not in self._store:
            return None
        self._store.move_to_end(key)
        return self._store[key]

    def put(self, key: str, value: Any) -> None:
        self._store[key] = value
        self._store.move_to_end(key)
        while len(self._store) > self.capacity:
            self._store.popitem(last=False)

    def evict(self, key: str) -> bool:
        return self._store.pop(key, None) is not None

    def clear(self) -> None:
        self._store.clear()

    def __len__(self) -> int:
        return len(self._store)

    def keys(self) -> list[str]:
        return list(self._store)


_avatar_cache: AvatarCache | None = None


def get_avatar_cache() -> AvatarCache:
    """Return the shared avatar cache singleton."""
    global _avatar_cache
    if _avatar_cache is None:
        _avatar_cache = AvatarCache()
    return _avatar_cache
