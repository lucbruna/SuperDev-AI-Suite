from __future__ import annotations

from typing import Any


class DatabaseMapper:
    """Maps database tables to model classes for ORM code generation."""

    def __init__(self) -> None:
        self._tables: dict[str, dict[str, Any]] = {}

    def map_table(
        self,
        name: str,
        columns: list[dict[str, Any]],
        model: str | None = None,
    ) -> str:
        self._tables[name] = {
            "table": name,
            "columns": columns,
            "model": model or self._to_model_name(name),
        }
        return name

    @staticmethod
    def _to_model_name(table: str) -> str:
        return "".join(word.capitalize() for word in table.replace("_", " ").split())

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

    def generate_mapping_code(self, table: str) -> str:
        tbl = self._tables.get(table)
        if tbl is None:
            return f"# Table '{table}' not found"
        model_name = tbl["model"]
        cols_code = "\n".join(f"    {c['name']}: {c.get('type', 'str')}" for c in tbl["columns"])
        return (
            f"from __future__ import annotations\n\nfrom sqlalchemy import Column, Integer, String\n"
            f"from sqlalchemy.orm import declarative_base\n\nBase = declarative_base()\n\n\n"
            f"class {model_name}(Base):\n"
            f'    __tablename__ = "{table}"\n\n{cols_code}\n'
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "tables": list(self._tables.values()),
            "table_count": self.table_count,
        }
