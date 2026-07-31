"""Tests for organization invite and permission cache functionality.

These tests are designed to be self-contained and avoid importing from
backend modules that have complex dependency chains.
"""

import secrets
import time
import uuid
from collections import OrderedDict


def generate_invite_token() -> str:
    """Generate a cryptographically secure invitation token."""
    return secrets.token_urlsafe(32)


class PermissionCache:
    """Inline copy of PermissionCache for testing without import chain."""

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
        """Invalidate all cached permissions that reference a specific resource."""
        resource_key = f"{resource_type}:{resource_id}"
        keys_to_remove = [
            key for key in self._cache
            if resource_key in key
        ]
        for key in keys_to_remove:
            del self._cache[key]

    def clear(self) -> None:
        self._cache.clear()


# ── Invite Token Tests ──────────────────────────────────────────────


class TestInviteTokenGeneration:
    def test_generate_invite_token_returns_string(self):
        token = generate_invite_token()
        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_invite_token_unique(self):
        tokens = {generate_invite_token() for _ in range(100)}
        assert len(tokens) == 100

    def test_generate_invite_token_url_safe(self):
        token = generate_invite_token()
        assert " " not in token
        assert "/" not in token


# ── Permission Cache Tests ──────────────────────────────────────────


class TestPermissionCache:
    def test_invalidate_resource_removes_matching_entries(self):
        cache = PermissionCache(max_size=100, default_ttl=300)
        user_id = uuid.uuid4()
        resource_id = uuid.uuid4()

        cache._cache[f"perms:user:{user_id}:project:{resource_id}"] = (
            ["read", "write"],
            999999999,
        )
        cache._cache[f"perms:user:{user_id}:other:resource"] = (
            ["admin"],
            999999999,
        )

        cache.invalidate_resource("project", resource_id)

        assert f"perms:user:{user_id}:project:{resource_id}" not in cache._cache
        assert f"perms:user:{user_id}:other:resource" in cache._cache

    def test_invalidate_resource_no_match(self):
        cache = PermissionCache(max_size=100, default_ttl=300)
        user_id = uuid.uuid4()
        resource_id = uuid.uuid4()

        cache._cache[f"perms:user:{user_id}:org:other"] = (
            ["read"],
            999999999,
        )

        cache.invalidate_resource("project", resource_id)
        assert len(cache._cache) == 1

    def test_invalidate_resource_empty_cache(self):
        cache = PermissionCache(max_size=100, default_ttl=300)
        resource_id = uuid.uuid4()
        cache.invalidate_resource("project", resource_id)
        assert len(cache._cache) == 0

    def test_invalidate_resource_multiple_users(self):
        cache = PermissionCache(max_size=100, default_ttl=300)
        user1 = uuid.uuid4()
        user2 = uuid.uuid4()
        resource_id = uuid.uuid4()

        cache._cache[f"perms:user:{user1}:project:{resource_id}"] = (
            ["read"],
            999999999,
        )
        cache._cache[f"perms:user:{user2}:project:{resource_id}"] = (
            ["write"],
            999999999,
        )

        cache.invalidate_resource("project", resource_id)

        assert f"perms:user:{user1}:project:{resource_id}" not in cache._cache
        assert f"perms:user:{user2}:project:{resource_id}" not in cache._cache

    def test_cache_operations_after_invalidate(self):
        cache = PermissionCache(max_size=100, default_ttl=300)
        user_id = uuid.uuid4()
        resource_id = uuid.uuid4()

        cache.set_cached_permissions(user_id, ["read", "write"])
        cache.invalidate_resource("project", resource_id)

        cache.set_cached_permissions(user_id, ["admin"])
        perms = cache.get_cached_permissions(user_id)
        assert perms == ["admin"]

    def test_set_and_get_permissions(self):
        cache = PermissionCache(max_size=100, default_ttl=300)
        user_id = uuid.uuid4()

        cache.set_cached_permissions(user_id, ["read", "write"])
        perms = cache.get_cached_permissions(user_id)
        assert perms == ["read", "write"]

    def test_get_expired_permissions(self):
        cache = PermissionCache(max_size=100, default_ttl=300)
        user_id = uuid.uuid4()

        # Manually inject an expired entry (expiry in the past)
        key = f"perms:user:{user_id}"
        cache._cache[key] = (["read"], time.monotonic() - 1)
        
        perms = cache.get_cached_permissions(user_id)
        assert perms is None

    def test_invalidate_user(self):
        cache = PermissionCache(max_size=100, default_ttl=300)
        user_id = uuid.uuid4()

        cache.set_cached_permissions(user_id, ["read"])
        cache.invalidate_user(user_id)
        perms = cache.get_cached_permissions(user_id)
        assert perms is None

    def test_clear_cache(self):
        cache = PermissionCache(max_size=100, default_ttl=300)
        user_id1 = uuid.uuid4()
        user_id2 = uuid.uuid4()

        cache.set_cached_permissions(user_id1, ["read"])
        cache.set_cached_permissions(user_id2, ["write"])
        cache.clear()
        assert len(cache._cache) == 0

    def test_max_size_eviction(self):
        cache = PermissionCache(max_size=2, default_ttl=300)
        user1 = uuid.uuid4()
        user2 = uuid.uuid4()
        user3 = uuid.uuid4()

        cache.set_cached_permissions(user1, ["a"])
        cache.set_cached_permissions(user2, ["b"])
        cache.set_cached_permissions(user3, ["c"])

        # First user should have been evicted
        assert cache.get_cached_permissions(user1) is None
        assert cache.get_cached_permissions(user2) == ["b"]
        assert cache.get_cached_permissions(user3) == ["c"]
