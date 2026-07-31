"""Log analysis (Volume 37, Fase 4)."""

from __future__ import annotations

from devops_engine.devops_models import LogEntry
from devops_engine.devops_protocols import rate, top_n


class LogAnalyzer:
    """Summarizes error rates and frequent failure messages."""

    def error_rate(self, entries: list[LogEntry]) -> float:
        errors = sum(1 for entry in entries if entry.level == "error")
        return rate(errors, len(entries))

    def top_errors(self, entries: list[LogEntry],
                   limit: int = 5) -> list[str]:
        counts: dict[str, int] = {}
        for entry in entries:
            if entry.level == "error":
                counts[entry.message] = counts.get(entry.message, 0) + 1
        return [message for message, _count in top_n(
            counts.items(), key=lambda item: item[1], limit=limit)]

    def summary(self, entries: list[LogEntry]) -> dict[str, int | float]:
        return {
            "total": len(entries),
            "errors": sum(1 for e in entries if e.level == "error"),
            "warnings": sum(1 for e in entries if e.level == "warning"),
            "error_rate": self.error_rate(entries),
        }
