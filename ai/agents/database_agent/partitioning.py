from __future__ import annotations

from typing import Any

PARTITION_STRATEGIES = {"range", "list", "hash"}


class Partitioning:
    """Manages database table partitioning strategies."""

    def __init__(self) -> None:
        self._strategies: dict[str, dict[str, Any]] = {}

    def add_strategy(self, table: str, strategy: str, column: str) -> str:
        strategy = strategy.lower()
        if strategy not in PARTITION_STRATEGIES:
            strategy = "range"
        self._strategies[table] = {
            "table": table,
            "strategy": strategy,
            "column": column,
        }
        return table

    def get_strategy(self, table: str) -> dict[str, Any] | None:
        return self._strategies.get(table)

    def remove_strategy(self, table: str) -> bool:
        if table in self._strategies:
            del self._strategies[table]
            return True
        return False

    def list_strategies(self) -> list[dict[str, Any]]:
        return list(self._strategies.values())

    @property
    def strategy_count(self) -> int:
        return len(self._strategies)

    def generate_partition_sql(self, table: str) -> str:
        strat = self._strategies.get(table)
        if strat is None:
            return f"-- No partitioning strategy for '{table}'"
        strategy = strat["strategy"]
        column = strat["column"]
        templates = {
            "range": (
                f"CREATE TABLE {table}_partitioned (\n"
                f"  LIKE {table} INCLUDING ALL\n"
                f") PARTITION BY RANGE ({column});\n\n"
                f"CREATE TABLE {table}_2024 PARTITION OF {table}_partitioned\n"
                f"  FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');\n"
            ),
            "list": (
                f"CREATE TABLE {table}_partitioned (\n"
                f"  LIKE {table} INCLUDING ALL\n"
                f") PARTITION BY LIST ({column});\n\n"
                f"CREATE TABLE {table}_east PARTITION OF {table}_partitioned\n"
                f"  FOR VALUES IN ('east');\n"
            ),
            "hash": (
                f"CREATE TABLE {table}_partitioned (\n"
                f"  LIKE {table} INCLUDING ALL\n"
                f") PARTITION BY HASH ({column});\n\n"
                f"CREATE TABLE {table}_p0 PARTITION OF {table}_partitioned\n"
                f"  FOR VALUES WITH (MODULUS 4, REMAINDER 0);\n"
            ),
        }
        return templates.get(strategy, templates["range"])

    def to_dict(self) -> dict[str, Any]:
        return {
            "strategies": list(self._strategies.values()),
            "strategy_count": self.strategy_count,
        }
