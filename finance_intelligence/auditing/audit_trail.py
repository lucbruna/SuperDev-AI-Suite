"""Audit trail for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

from typing import Any

from finance_intelligence.finance_events import (FinanceEventType,
                                                 FinanceEvents)
from finance_intelligence.finance_models import AuditLog
from finance_intelligence.finance_protocols import new_id, now
from finance_intelligence.finance_registry import FinanceRegistry


class AuditTrail:
    """Immutable audit log recording financial operations."""

    def __init__(self, registry: FinanceRegistry | None = None,
                 events: FinanceEvents | None = None) -> None:
        self.registry = registry or FinanceRegistry()
        self.events = events or FinanceEvents()

    def record(self, event: str, actor: str = "system",
               target: str = "",
               detail: dict[str, Any] | None = None,
               created_at: float | None = None) -> AuditLog:
        audit = AuditLog(
            audit_id=new_id("audit"), event=event, actor=actor,
            target=target, detail=dict(detail or {}),
            created_at=created_at if created_at is not None else now())
        self.registry.record_audit(audit)
        self.events.publish(FinanceEventType.AUDIT_RECORDED,
                            {"audit_id": audit.audit_id, "event": event,
                             "actor": actor})
        return audit

    def list(self) -> list[AuditLog]:
        return self.registry.list_audits()

    def by_actor(self, actor: str) -> list[AuditLog]:
        return [audit for audit in self.list()
                if audit.actor.lower() == actor.lower()]

    def by_event(self, event: str) -> list[AuditLog]:
        return [audit for audit in self.list()
                if audit.event.lower() == event.lower()]

    def recent(self, limit: int = 50) -> list[AuditLog]:
        return sorted(self.list(), key=lambda audit: audit.created_at,
                      reverse=True)[:max(0, limit)]

    def count(self) -> int:
        return self.registry.count_audits()
