"""HealingPolicy: maps failure sources to remediation plans and retry limits."""
from __future__ import annotations

from typing import Any, Optional

from aios.self_healing.remediation import RemediationPlan


class HealingPolicy:
    """Deterministic lookup of the plan (and retry budget) for a failure source."""

    def __init__(self) -> None:
        self._plans: dict[str, RemediationPlan] = {}
        self._retries: dict[str, int] = {}

    def add(
        self, source: str, plan: RemediationPlan, retry_limit: int = 1
    ) -> bool:
        if source in self._plans:
            raise KeyError(f"policy for source {source!r} already registered")
        self._plans[source] = plan
        self._retries[source] = max(0, int(retry_limit))
        return True

    def plan_for(self, source: str) -> Optional[RemediationPlan]:
        return self._plans.get(source)

    def retry_limit(self, source: str) -> int:
        return self._retries.get(source, 0)

    def sources(self) -> list[str]:
        return sorted(self._plans)

    def snapshot(self) -> dict[str, Any]:
        return {
            "sources": self.sources(),
            "plans": [self._plans[source].to_dict() for source in self.sources()],
            "retries": {source: self._retries[source] for source in self.sources()},
        }
