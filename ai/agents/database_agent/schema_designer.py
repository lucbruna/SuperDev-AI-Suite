from __future__ import annotations

from typing import Any


class SchemaDesigner:
    """Designs and manages database schema tables."""

    def __init__(self) -> None:
        self._tables: dict[str, dict[str, Any]] = {}

    def add_table(
        self,
        name: str,
        columns: list[dict[str, Any]],
        primary_key: str = "id",
    ) -> str:
        self._tables[name] = {
            "name": name,
            "columns": columns,
            "primary_key": primary_key,
            "foreign_keys": [],
        }
        return name

    def get_table(self, name: str) -> dict[str, Any] | None:
        return self._tables.get(name)

    def remove_table(self, name: str) -> bool:
        if name in self._tables:
            del self._tables[name]
            return True
        return False

    def list_tables(self) -> list[dict[str, Any]]:
        return list(self._tables.values())

    @property
    def table_count(self) -> int:
        return len(self._tables)

    def add_foreign_key(
        self, table: str, column: str, ref_table: str, ref_column: str
    ) -> bool:
        tbl = self._tables.get(table)
        if tbl is None:
            return False
        tbl["foreign_keys"].append({
            "column": column,
            "ref_table": ref_table,
            "ref_column": ref_column,
        })
        return True

    def generate_ddl(self, name: str) -> str:
        tbl = self._tables.get(name)
        if tbl is None:
            return f"-- Table '{name}' not found"
        col_lines = "\n  ".join(
            f"{c['name']} {c.get('type', 'VARCHAR(255)')}"
            for c in tbl["columns"]
        )
        fk_lines = "\n".join(
            f",\n  FOREIGN KEY ({fk['column']}) REFERENCES {fk['ref_table']}({fk['ref_column']})"
            for fk in tbl["foreign_keys"]
        )
        return (
            f"CREATE TABLE {name} (\n"
            f"  {col_lines}"
            f"{fk_lines}\n"
            f");\n"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "tables": list(self._tables.values()),
            "table_count": self.table_count,
        }
