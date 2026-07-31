from __future__ import annotations

from typing import Any


class QueryOptimizer:
    """Analyzes and optimizes database queries."""

    SLOW_PATTERNS: list[tuple[str, str, str]] = [
        ("SELECT *", "Avoid SELECT *; specify columns explicitly", "low"),
        ("NOT IN", "Prefer NOT EXISTS over NOT IN", "medium"),
        ("OR", "Consider using UNION instead of multiple OR", "low"),
        ("LIKE '%", "Leading wildcard prevents index usage", "high"),
        ("COUNT(*)", "Consider indexed count alternatives", "low"),
        ("ORDER BY RAND()", "Avoid ORDER BY RAND(); use alternatives", "high"),
        ("DISTINCT", "Check if DISTINCT is necessary", "low"),
    ]

    def __init__(self) -> None:
        self._queries: dict[str, dict[str, Any]] = {}

    def add_query(self, name: str, sql: str, execution_time_ms: float = 0) -> str:
        self._queries[name] = {
            "name": name,
            "sql": sql,
            "execution_time_ms": execution_time_ms,
        }
        return name

    def get_query(self, name: str) -> dict[str, Any] | None:
        return self._queries.get(name)

    def list_queries(self) -> list[dict[str, Any]]:
        return list(self._queries.values())

    @property
    def query_count(self) -> int:
        return len(self._queries)

    def analyze_query(self, sql: str) -> list[dict[str, Any]]:
        suggestions = []
        for pattern, advice, severity in self.SLOW_PATTERNS:
            if pattern.lower() in sql.lower():
                suggestions.append(
                    {
                        "pattern": pattern,
                        "advice": advice,
                        "severity": severity,
                    }
                )
        return suggestions

    def suggest_indexes(self, sql: str) -> list[str]:
        import re

        columns = re.findall(r"\bWHERE\s+(\w+)", sql, re.IGNORECASE)
        columns += re.findall(r"\bJOIN\s+\w+\s+ON\s+\w+\.(\w+)", sql, re.IGNORECASE)
        columns += re.findall(r"\bORDER BY\s+(\w+)", sql, re.IGNORECASE)
        return list(set(f"idx_{col}" for col in columns if col))

    def to_dict(self) -> dict[str, Any]:
        return {
            "queries": list(self._queries.values()),
            "query_count": self.query_count,
        }
