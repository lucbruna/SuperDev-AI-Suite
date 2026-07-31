"""Audit reports for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

from typing import Any

from finance_intelligence.finance_models import AuditLog


class AuditReports:
    """Summarize audit activity for reporting and review."""

    def summary(self, audits: list[AuditLog]) -> dict[str, Any]:
        return {
            "total": len(audits),
            "actors": len({audit.actor for audit in audits}),
            "events": len({audit.event for audit in audits}),
        }

    def by_actor(self, audits: list[AuditLog]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for audit in audits:
            counts[audit.actor] = counts.get(audit.actor, 0) + 1
        return counts

    def by_event(self, audits: list[AuditLog]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for audit in audits:
            counts[audit.event] = counts.get(audit.event, 0) + 1
        return counts

    def window(self, audits: list[AuditLog],
               start: float = 0.0, end: float = 0.0) -> list[AuditLog]:
        filtered = [audit for audit in audits
                    if (not start or audit.created_at >= start)
                    and (not end or audit.created_at <= end)]
        return sorted(filtered, key=lambda audit: audit.created_at)
