"""Graph edge model — normalized, direction-aware relations.

Edges reference node ids and carry a relation label plus optional line/weight
metadata. Relation names are constants here so later phases (dependency
analyzer, relations) reuse the same vocabulary.
"""
from __future__ import annotations

from typing import Any

CONTAINS = "contains"
IMPORTS = "imports"
CALLS = "calls"
REFERENCES = "references"
DEPENDS_ON = "depends_on"


def make_edge(
    source: str,
    target: str,
    relation: str,
    *,
    line: int | None = None,
    weight: float = 1.0,
    **meta: Any,
) -> dict[str, Any]:
    """Build a normalized edge dict (``None`` extras are dropped)."""
    edge: dict[str, Any] = {
        "source": source,
        "target": target,
        "relation": relation,
        "weight": float(weight),
    }
    if line is not None:
        edge["line"] = int(line)
    edge.update({key: value for key, value in meta.items() if value is not None})
    return edge
