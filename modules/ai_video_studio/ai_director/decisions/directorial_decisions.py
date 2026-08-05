"""Directorial decisions — aggregates creative decisions for a production."""
from __future__ import annotations

from typing import Any


class DirectorialDecisions:
    """Collects and logs all directorial decisions."""

    def __init__(self) -> None:
        self._decisions: list[dict[str, Any]] = []

    def record(self, decision: dict[str, Any]) -> None:
        self._decisions.append(decision)

    def all(self) -> list[dict[str, Any]]:
        return list(self._decisions)


_directorial_decisions: DirectorialDecisions | None = None


def get_directorial_decisions() -> DirectorialDecisions:
    global _directorial_decisions
    if _directorial_decisions is None:
        _directorial_decisions = DirectorialDecisions()
    return _directorial_decisions
