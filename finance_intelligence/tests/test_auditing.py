"""Tests for the auditing subsystem (Volume 35, Fase 5)."""

from __future__ import annotations

import pytest

from finance_intelligence.auditing.audit_engine import AuditEngine
from finance_intelligence.finance_events import FinanceEventType
from finance_intelligence.finance_models import (RiskLevel, Transaction,
                                                 TransactionStatus,
                                                 TransactionType)
from finance_intelligence.finance_protocols import new_id


@pytest.fixture()
def engine() -> AuditEngine:
    return AuditEngine()


def make_transaction(status: TransactionStatus = TransactionStatus.PENDING,
                     ) -> Transaction:
    return Transaction(
        transaction_id=new_id("tx"),
        kind=TransactionType.EXPENSE, amount=100.0, status=status)


class TestAuditTrail:
    def test_record(self, engine: AuditEngine) -> None:
        audit = engine.record("payment.executed", actor="finance",
                              target="pay-1")
        assert audit.event == "payment.executed"
        assert audit.actor == "finance"
        assert engine.trail.count() == 1

    def test_record_publishes_event(self, engine: AuditEngine) -> None:
        seen: list[dict] = []
        engine.events.on(FinanceEventType.AUDIT_RECORDED, seen.append)
        engine.record("payment.executed", actor="finance")
        assert len(seen) == 1
        assert seen[0]["actor"] == "finance"

    def test_by_actor(self, engine: AuditEngine) -> None:
        engine.record("a", actor="finance")
        engine.record("b", actor="admin")
        assert len(engine.trail.by_actor("FINANCE")) == 1

    def test_by_event(self, engine: AuditEngine) -> None:
        engine.record("payment.executed", actor="finance")
        engine.record("payment.failed", actor="admin")
        assert len(engine.trail.by_event("payment.executed")) == 1

    def test_recent_orders_newest_first(self, engine: AuditEngine) -> None:
        first = engine.record("first", created_at=100.0)
        second = engine.record("second", created_at=200.0)
        recent = engine.trail.recent()
        assert recent[0].audit_id == second.audit_id
        assert recent[1].audit_id == first.audit_id

    def test_detail_preserved(self, engine: AuditEngine) -> None:
        audit = engine.record("approve", detail={"amount": 500.0})
        assert audit.detail["amount"] == 500.0


class TestAuditReports:
    def test_summary(self, engine: AuditEngine) -> None:
        engine.record("a", actor="finance")
        engine.record("b", actor="finance")
        engine.record("c", actor="admin")
        summary = engine.reports.summary(engine.trail.list())
        assert summary["total"] == 3
        assert summary["actors"] == 2
        assert summary["events"] == 3

    def test_by_actor_and_event(self, engine: AuditEngine) -> None:
        engine.record("run", actor="finance")
        engine.record("run", actor="finance")
        engine.record("stop", actor="admin")
        by_actor = engine.reports.by_actor(engine.trail.list())
        assert by_actor["finance"] == 2
        by_event = engine.reports.by_event(engine.trail.list())
        assert by_event["run"] == 2

    def test_window(self, engine: AuditEngine) -> None:
        first = engine.record("first", created_at=100.0)
        engine.record("second", created_at=200.0)
        window = engine.reports.window(engine.trail.list(),
                                       start=99.0, end=100.5)
        assert [audit.audit_id for audit in window] == [first.audit_id]


class TestCompliance:
    def test_empty_registry_compliant(self, engine: AuditEngine) -> None:
        assert engine.is_compliant() is True
        assert engine.status() == "compliant"

    def test_pending_transaction_fails(self, engine: AuditEngine) -> None:
        engine.registry.register_transaction(make_transaction())
        assert engine.is_compliant() is False
        assert engine.status() == "non_compliant"

    def test_open_alert_attention(self, engine: AuditEngine) -> None:
        alert = engine.registry.register_alert  # noqa: F841
        from finance_intelligence.finance_models import FinancialAlert
        engine.registry.register_alert(FinancialAlert(
            alert_id=new_id("alert"), message="risk"))
        assert engine.is_compliant() is True
        assert engine.status() == "attention"

    def test_approved_transactions_compliant(self, engine: AuditEngine) -> None:
        engine.registry.register_transaction(
            make_transaction(TransactionStatus.APPROVED))
        assert engine.is_compliant() is True


class TestAuditEngine:
    def test_stats(self, engine: AuditEngine) -> None:
        engine.record("a", actor="finance")
        stats = engine.stats()
        assert stats["audits"] == 1
        assert stats["actors"] == 1
        assert stats["compliance_status"] == "compliant"

    def test_findings(self, engine: AuditEngine) -> None:
        engine.registry.register_transaction(make_transaction())
        findings = engine.findings()
        assert any(finding["status"] == "fail"
                   for finding in findings)
