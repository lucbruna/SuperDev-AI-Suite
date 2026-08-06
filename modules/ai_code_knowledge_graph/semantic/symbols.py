"""Symbol index — name → definition locations across a scan.

Built from parsed entities, the index lets later phases (dependency analyzer,
RAG, agents) answer "where is X defined?" and "which files mention X?" without
re-parsing source. Definitions cover the node kinds that declare names.
"""
from __future__ import annotations

from typing import Any

_DEFINITION_KINDS = (
    "class",
    "function",
    "method",
    "interface",
    "type",
    "enum",
    "table",
    "view",
    "plugin",
    "workflow",
)


class SymbolIndex:
    """Immutable-ish lookup of symbol definitions by name."""

    def __init__(self, definitions: dict[str, list[dict[str, Any]]] | None = None) -> None:
        self._definitions: dict[str, list[dict[str, Any]]] = definitions or {}

    @classmethod
    def from_scan(cls, scan_result: dict[str, Any]) -> "SymbolIndex":
        """Build an index from a scanner result (files with parsed entities)."""
        definitions: dict[str, list[dict[str, Any]]] = {}
        for entry in scan_result.get("files", []):
            rel_path = entry.get("rel_path", "")
            parsed = entry.get("parsed")
            if not isinstance(parsed, dict):
                continue
            for entity in parsed.get("entities", []):
                kind = entity.get("kind")
                if kind not in _DEFINITION_KINDS:
                    continue
                name = entity.get("name")
                if not name:
                    continue
                definitions.setdefault(name, []).append(
                    {
                        "file": rel_path,
                        "kind": kind,
                        "line": entity.get("start_line", 1),
                    }
                )
        return cls(definitions)

    def lookup(self, name: str) -> list[dict[str, Any]]:
        """Return definition locations for a symbol name (empty when absent)."""
        return list(self._definitions.get(name, []))

    def definitions(self) -> dict[str, list[dict[str, Any]]]:
        """Return a copy of the full name → locations mapping."""
        return {name: list(locations) for name, locations in self._definitions.items()}

    def names(self) -> list[str]:
        return sorted(self._definitions)

    def count(self) -> int:
        return len(self._definitions)

    def top(self, limit: int = 20) -> dict[str, int]:
        """Most-referenced symbol names (by number of definition sites)."""
        ranked = sorted(self._definitions.items(), key=lambda item: len(item[1]), reverse=True)
        return {name: len(locations) for name, locations in ranked[:limit]}
