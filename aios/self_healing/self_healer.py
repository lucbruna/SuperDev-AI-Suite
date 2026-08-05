"""SelfHealer: detects failures, opens incidents, and applies remediation."""
from __future__ import annotations

from typing import Any, Optional

from aios.self_healing.failure_detector import FailureDetector, FailureReport
from aios.self_healing.healing_policy import HealingPolicy
from aios.self_healing.incident import Incident, INCIDENT_STATUSES
from aios.self_healing.remediation import RemediationPlan


class SelfHealer:
    """Tick-driven loop: detect -> incident (deduped) -> remediate with retries."""

    def __init__(
        self,
        detector: FailureDetector | None = None,
        policy: HealingPolicy | None = None,
    ) -> None:
        self.detector = detector if detector is not None else FailureDetector()
        self.policy = policy if policy is not None else HealingPolicy()
        self._incidents: dict[str, Incident] = {}
        self._seq = 0

    def tick(self, context: dict[str, Any] | None = None) -> FailureReport:
        """Run checks and remediate new failures. Returns the failure report."""
        report = self.detector.run_all()
        ctx = dict(context or {})
        for source in report.failing:
            if any(
                incident.source == source and incident.status == "open"
                for incident in self._incidents.values()
            ):
                continue  # dedupe: an open incident already covers this source
            self._open_and_remediate(source, report, ctx)
        return report

    def _open_and_remediate(
        self, source: str, report: FailureReport, ctx: dict[str, Any]
    ) -> None:
        self._seq += 1
        critical = source in report.critical
        incident = Incident(
            incident_id=f"inc-{self._seq:04d}",
            source=source,
            critical=critical,
            message=f"health check {source!r} failed",
            created_seq=self._seq,
        )
        self._incidents[incident.incident_id] = incident
        plan = self.policy.plan_for(source)
        if plan is None:
            return
        limit = self.policy.retry_limit(source)
        for _ in range(limit + 1):
            incident.attempts += 1
            outcome = plan.execute(ctx)
            if outcome.ok:
                incident.status = "resolved"
                incident.resolved_seq = self._seq
                incident.actions_applied = list(outcome.applied)
                return
        incident.status = "open"  # remediation exhausted; incident remains open

    def incidents(self) -> list[Incident]:
        return [self._incidents[key] for key in sorted(self._incidents)]

    def open_incidents(self) -> list[Incident]:
        return [
            incident
            for incident in self.incidents()
            if incident.status == "open"
        ]

    def resolved_count(self) -> int:
        return sum(1 for incident in self.incidents() if incident.status == "resolved")

    def snapshot(self) -> dict[str, Any]:
        return {
            "incidents": [incident.to_dict() for incident in self.incidents()],
            "open": len(self.open_incidents()),
            "resolved": self.resolved_count(),
            "policy": self.policy.snapshot(),
        }
