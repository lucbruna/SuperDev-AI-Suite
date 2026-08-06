"""MemoryStore — namespaced long-term orchestrator memory.

Deterministic, in-memory key-value storage with versioning: every write
increments a version for the key. ``snapshot()``/``restore()`` allow the
orchestrator to persist and reload memory across restarts.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class MemoryEntry:
    """A stored value with a monotonic version."""

    value: Any
    version: int = 0


class MemoryStore:
    """Namespaced memory: ``namespace -> key -> MemoryEntry``.

    Attributes:
        entries: storage; iteration order reflects insertion (deterministic).
    """

    def __init__(self) -> None:
        self.entries: dict[str, dict[str, MemoryEntry]] = {}

    def remember(self, namespace: str, key: str, value: Any) -> MemoryEntry:
        ns = self.entries.setdefault(namespace, {})
        entry = ns.get(key)
        if entry is None:
            entry = MemoryEntry(value=value, version=1)
            ns[key] = entry
        else:
            entry.value = value
            entry.version += 1
        return entry

    def recall(self, namespace: str, key: str, default: Any = None) -> Any:
        ns = self.entries.get(namespace)
        if ns is None:
            return default
        entry = ns.get(key)
        return entry.value if entry is not None else default

    def version(self, namespace: str, key: str) -> int:
        ns = self.entries.get(namespace)
        if ns is None:
            return 0
        entry = ns.get(key)
        return entry.version if entry is not None else 0

    def forget(self, namespace: str, key: str) -> bool:
        ns = self.entries.get(namespace)
        if ns is None:
            return False
        return ns.pop(key, None) is not None

    def namespaces(self) -> tuple[str, ...]:
        return tuple(self.entries.keys())

    def keys(self, namespace: str) -> tuple[str, ...]:
        ns = self.entries.get(namespace)
        return tuple(ns.keys()) if ns is not None else ()

    def entries_in(self, namespace: str) -> tuple[tuple[str, Any], ...]:
        ns = self.entries.get(namespace)
        if ns is None:
            return ()
        return tuple((k, e.value) for k, e in ns.items())

    def snapshot(self) -> dict[str, dict[str, dict[str, Any]]]:
        return {
            ns: {k: {"value": e.value, "version": e.version} for k, e in items.items()}
            for ns, items in self.entries.items()
        }

    def restore(self, snapshot: dict[str, dict[str, dict[str, Any]]]) -> None:
        self.entries = {
            ns: {
                k: MemoryEntry(value=d["value"], version=d["version"])
                for k, d in items.items()
            }
            for ns, items in snapshot.items()
        }

    def clear(self) -> None:
        self.entries.clear()
