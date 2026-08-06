"""Graph node model — stable, deterministic node identifiers and builders.

Node ids are deterministic (``kind:file:name:line``) so edges stay stable
across rebuilds and snapshots can be diffed. File nodes use a compact id
(``file:<rel_path>``). ``None`` extras are dropped to keep payloads lean.
"""
from __future__ import annotations

from typing import Any

_ENTITY_KEYS = frozenset({"id", "kind", "name", "file", "start_line", "end_line"})


def file_node_id(rel_path: str) -> str:
    """Stable id for a file node."""
    return f"file:{rel_path}"


def node_id(kind: str, file: str, name: str = "", line: int | None = None) -> str:
    """Stable, collision-resistant id for an entity node."""
    parts = [kind, str(file), str(name) if name not in (None, "") else "<unnamed>"]
    if line is not None:
        parts.append(str(line))
    return ":".join(parts)


def make_node(
    kind: str,
    name: str,
    file: str,
    start_line: int = 1,
    end_line: int | None = None,
    **meta: Any,
) -> dict[str, Any]:
    """Build a normalized node dict (``None`` extras are dropped)."""
    end = end_line if end_line is not None else start_line
    node: dict[str, Any] = {
        "id": node_id(kind, file, name, start_line),
        "kind": kind,
        "name": name,
        "file": file,
        "start_line": int(start_line),
        "end_line": int(end),
    }
    node.update({key: value for key, value in meta.items() if value is not None})
    return node


def make_file_node(rel_path: str, **meta: Any) -> dict[str, Any]:
    """Build a file node with the compact ``file:<rel_path>`` id."""
    node = make_node("file", rel_path, rel_path, 1, 1, **meta)
    node["id"] = file_node_id(rel_path)
    return node


def extra_meta(entity: dict[str, Any]) -> dict[str, Any]:
    """Return entity fields beyond the canonical schema (for node extras)."""
    return {key: value for key, value in entity.items() if key not in _ENTITY_KEYS}
