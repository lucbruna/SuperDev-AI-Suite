"""Runbook management for recovery (Volume 37, Fase 5)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from devops_engine.devops_models import Severity
from devops_engine.devops_protocols import new_id, now


@dataclass
class Runbook:
    """A recovery runbook with ordered steps."""
    runbook_id: str
    name: str
    steps: list[str] = field(default_factory=list)
    severity: Severity = Severity.WARNING
    created_at: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class RunbookManager:
    """Creates and serves recovery runbooks."""

    def __init__(self) -> None:
        self._runbooks: dict[str, Runbook] = {}

    def create(self, name: str, steps: list[str] | None = None,
               severity: Severity = Severity.WARNING) -> Runbook:
        runbook = Runbook(
            runbook_id=new_id("runbook"),
            name=name,
            steps=list(steps or []),
            severity=severity,
            created_at=now(),
        )
        self._runbooks[runbook.runbook_id] = runbook
        return runbook

    def get(self, runbook_id: str) -> Runbook | None:
        return self._runbooks.get(runbook_id)

    def steps_for(self, severity: Severity) -> list[Runbook]:
        return [runbook for runbook in self._runbooks.values()
                if runbook.severity == severity]

    def list(self) -> list[Runbook]:
        return list(self._runbooks.values())

    def count(self) -> int:
        return len(self._runbooks)
