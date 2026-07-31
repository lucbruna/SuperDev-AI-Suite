from __future__ import annotations

from .temporary_storage import TemporaryStorage


class Expiration:
    """TTL-based expiration management for short-term memory."""

    def __init__(self, default_ttl: float = 300.0):
        self._default_ttl = default_ttl

    @property
    def default_ttl(self) -> float:
        return self._default_ttl

    def purge_expired(self, storage: TemporaryStorage) -> int:
        return storage.purge_expired()

    def is_expired(self, age: float, ttl: float) -> bool:
        return age >= ttl

    def remaining_ttl(self, age: float, ttl: float) -> float:
        remaining = ttl - age
        return max(0.0, remaining)
