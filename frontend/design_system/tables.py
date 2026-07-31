from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ColumnSpec:
    """Definition of a table column."""

    key: str
    title: str
    sortable: bool = False
    width: str | None = None
    renderer: str | None = None


class Tables:
    """Builds table definitions."""

    def __init__(self) -> None:
        self._templates: dict[str, list[ColumnSpec]] = {}

    def column(self, key: str, title: str, **kwargs: Any) -> ColumnSpec:
        return ColumnSpec(key=key, title=title, **kwargs)

    def register_template(self, name: str, columns: list[ColumnSpec]) -> None:
        self._templates[name] = columns

    def template(self, name: str) -> list[ColumnSpec]:
        if name not in self._templates:
            raise KeyError(f"unknown table template: {name}")
        return self._templates[name]

    def build_table(self, name: str, rows: list[dict[str, Any]], **props: Any) -> dict[str, Any]:
        return {
            "type": "table",
            "name": name,
            "columns": [vars(c) for c in self.template(name)],
            "rows": rows,
            "props": props,
        }

    def sort(self, name: str, rows: list[dict[str, Any]], key: str, reverse: bool = False) -> list[dict[str, Any]]:
        columns = {c.key for c in self.template(name)}
        if key not in columns:
            raise KeyError(f"column not in table template: {key}")
        return sorted(rows, key=lambda row: row.get(key, ""), reverse=reverse)
