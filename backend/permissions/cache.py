from __future__ import annotations

import time
import uuid
from collections import OrderedDict


class PermissionCache:
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        self._cache: OrderedDict[str, tuple[list[str], float]] = OrderedDict()
        self._max_size = max_size
        self._default_ttl = default_ttl

    def _cached_permissions_key(self, user_id: uuid.UUID) -> str:
        return f"perms:user:{user_id}"

    def get_cached_permissions(self, user_id: uuid.UUID) -> list[str] | None:
        key = self._cached_permissions_key(user_id)
        entry = self._cache.get(key)
        if entry is None:
            return None
        permissions, expiry = entry
        if time.monotonic() > expiry:
            del self._cache[key]
            return None
        self._cache.move_to_end(key)
        return permissions

    def set_cached_permissions(
        self, user_id: uuid.UUID, permissions: list[str], ttl: int | None = None
    ) -> None:
        key = self._cached_permissions_key(user_id)
        expiry = time.monotonic() + (ttl if ttl is not None else self._default_ttl)
        self._cache[key] = (permissions, expiry)
        self._cache.move_to_end(key)
        if len(self._cache) > self._max_size:
            self._cache.popitem(last=False)

    def invalidate_user(self, user_id: uuid.UUID) -> None:
        key = self._cached_permissions_key(user_id)
        self._cache.pop(key, None)

    def invalidate_resource(self, resource_type: str, resource_id: uuid.UUID) -> None:
        """Invalidate all cached permissions that reference a specific resource.

        Scans the cache and removes entries where the permission string contains
        the resource identifier (e.g., 'project:{id}' or 'org:{id}').
        """
        resource_key = f"{resource_type}:{resource_id}"
        keys_to_remove = [
            key for key in self._cache
            if resource_key in key
        ]
        for key in keys_to_remove:
            del self._cache[key]

    def clear(self) -> None:
        self._cache.clear()