from __future__ import annotations

from .memory_exceptions import MemoryValidationError
from .memory_models import MemoryEntry
from .memory_types import MemoryData, MemoryID, Tags


class MemoryValidator:
    """Validation logic for memory data integrity and constraints."""

    def __init__(self):
        self._errors: list[str] = []

    @property
    def errors(self) -> list[str]:
        return list(self._errors)

    def validate_entry(self, entry: MemoryEntry) -> bool:
        self._errors.clear()
        self._check_key(entry.key)
        self._check_data(entry.data)
        self._check_ttl(entry.ttl)
        return len(self._errors) == 0

    def validate_key(self, key: MemoryID) -> bool:
        self._errors.clear()
        self._check_key(key)
        return len(self._errors) == 0

    def validate_data(self, data: MemoryData) -> bool:
        self._errors.clear()
        self._check_data(data)
        return len(self._errors) == 0

    def validate_tags(self, tags: Tags) -> bool:
        self._errors.clear()
        if not isinstance(tags, list):
            self._errors.append("Tags must be a list")
        else:
            for tag in tags:
                if not isinstance(tag, str) or not tag.strip():
                    self._errors.append(f"Invalid tag: {tag!r}")
        return len(self._errors) == 0

    def _check_key(self, key: MemoryID) -> None:
        if not key or not isinstance(key, str):
            self._errors.append("Key must be a non-empty string")
        elif len(key) > 1024:
            self._errors.append("Key exceeds maximum length of 1024 characters")
        elif not key.strip():
            self._errors.append("Key must not be whitespace-only")

    def _check_data(self, data: MemoryData) -> None:
        if not isinstance(data, dict):
            self._errors.append("Data must be a dictionary")
            return
        import json
        try:
            size = len(json.dumps(data).encode("utf-8"))
            if size > 10 * 1024 * 1024:
                self._errors.append(f"Data size ({size} bytes) exceeds 10MB limit")
        except (TypeError, ValueError):
            self._errors.append("Data must be JSON-serializable")

    def _check_ttl(self, ttl: float | None) -> None:
        if ttl is not None and (not isinstance(ttl, (int, float)) or ttl < 0):
            self._errors.append("TTL must be a non-negative number")

    def raise_if_invalid(self) -> None:
        if self._errors:
            raise MemoryValidationError("; ".join(self._errors))

    def clear(self) -> None:
        self._errors.clear()
