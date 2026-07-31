"""Tests for the receivables subsystem (Volume 35, Fase 3)."""

from __future__ import annotations

import time

from finance_intelligence.finance_events import (FinanceEventType,
                                                 FinanceEvents)
from finance_intelligence.finance_metrics import FinanceMetrics
from finance_intelligence.finance_models import InvoiceStatus
from finance_intelligence.finance_registry import FinanceRegistry
from finance_intelligence.receivables import (Collection, CustomerDebt,
                                              InvoiceManager,
                                              PaymentPrediction,
                                              ReceivableEngine)


class TestInvoiceManager:
    def _manager(self):
        return InvoiceManager(FinanceEvents(), FinanceMetrics())

    def test_issue(self):
        manager = self._manager()
        invoice = manager.issue("Cliente A", 1500.0, due_date=time.time())
        assert invoice.invoice_id.startswith("invoice-")
        assert invoice.status == InvoiceStatus.ISSUED
        assert invoice.outstanding() == 1500.0

    def test_partial_then_paid(self):
        manager = self._manager()
        invoice = manager.issue("Cliente B", 1000.0)
        result = manager.register_payment(invoice.invoice_id, 400.0)
        assert result["status"] == "partial"
        assert invoice.status == InvoiceStatus.PARTIAL
        result = manager.register_payment(invoice.invoice_id, 600.0)
        assert result["status"] == "paid"
        assert invoice.status == InvoiceStatus.PAID
        assert invoice.outstanding() == 0.0

    def test_publishes_paid_event(self):
        events = FinanceEvents()
        fired = []
        events.on(FinanceEventType.INVOICE_PAID,
                  lambda payload: fired.append(payload))
        manager = InvoiceManager(events, FinanceMetrics())
        invoice = manager.issue("Cliente C", 500.0)
        manager.register_payment(invoice.invoice_id, 500.0)
        assert len(fired) == 1

    def test_mark_overdue(self):
        manager = self._manager()
        past = time.time() - 86400
        future = time.time() + 86400
        overdue = manager.issue("A", 100.0, due_date=past)
        pending = manager.issue("B", 100.0, due_date=future)
        count = manager.mark_overdue()
        assert count == 1
        assert overdue.status == InvoiceStatus.OVERDUE
        assert pending.status == InvoiceStatus.ISSUED


class TestCollection:
    def test_record_and_list(self):
        collection = Collection()
        invoice = InvoiceManager(FinanceEvents(), FinanceMetrics()).issue(
            "Cliente A", 100.0)
        attempt = collection.record_attempt(invoice, "email", "no_response",
                                            "cobrança 1")
        assert attempt["invoice_id"] == invoice.invoice_id
        assert len(collection.list_attempts()) == 1
        assert len(collection.attempts_for(invoice.invoice_id)) == 1

    def test_overdue_list(self):
        collection = Collection()
        manager = InvoiceManager(FinanceEvents(), FinanceMetrics())
        past = time.time() - 86400
        overdue = manager.issue("A", 100.0, due_date=past)
        future = manager.issue("B", 100.0, due_date=time.time() + 86400)
        overdue_list = collection.overdue_list(manager.list())
        assert overdue.invoice_id in [i.invoice_id for i in overdue_list]
        assert future.invoice_id not in [
            i.invoice_id for i in overdue_list]

    def test_status_overview(self):
        collection = Collection()
        manager = InvoiceManager(FinanceEvents(), FinanceMetrics())
        manager.issue("A", 100.0)
        overview = collection.status_overview(manager.list())
        assert overview.get("issued") == 1


class TestCustomerDebt:
    def test_outstanding_by_customer(self):
        debt = CustomerDebt()
        manager = InvoiceManager(FinanceEvents(), FinanceMetrics())
        manager.issue("Cliente A", 1000.0)
        manager.issue("Cliente A", 500.0)
        manager.issue("Cliente B", 300.0)
        balances = debt.outstanding_by_customer(manager.list())
        assert balances["Cliente A"] == 1500.0
        assert balances["Cliente B"] == 300.0

    def test_top_debtors(self):
        debt = CustomerDebt()
        manager = InvoiceManager(FinanceEvents(), FinanceMetrics())
        manager.issue("A", 100.0)
        manager.issue("B", 900.0)
        manager.issue("C", 500.0)
        top = debt.top_debtors(manager.list(), limit=2)
        assert top[0]["customer"] == "B"
        assert top[1]["customer"] == "C"

    def test_total_outstanding(self):
        debt = CustomerDebt()
        manager = InvoiceManager(FinanceEvents(), FinanceMetrics())
        invoice = manager.issue("A", 1000.0)
        manager.register_payment(invoice.invoice_id, 400.0)
        assert debt.total_outstanding(manager.list()) == 600.0


class TestPaymentPrediction:
    def test_healthy_invoice(self):
        prediction = PaymentPrediction()
        manager = InvoiceManager(FinanceEvents(), FinanceMetrics())
        invoice = manager.issue("A", 1000.0,
                                due_date=time.time() + 86400)
        result = prediction.predict(invoice)
        assert result["score"] >= 0.8

    def test_overdue_drops_score(self):
        prediction = PaymentPrediction()
        manager = InvoiceManager(FinanceEvents(), FinanceMetrics())
        invoice = manager.issue("A", 1000.0,
                                due_date=time.time() - 30 * 86400)
        result = prediction.predict(invoice)
        assert result["score"] < 0.7

    def test_at_risk(self):
        prediction = PaymentPrediction()
        manager = InvoiceManager(FinanceEvents(), FinanceMetrics())
        manager.issue("Risco", 20000.0,
                      due_date=time.time() - 60 * 86400)
        manager.issue("Saudável", 500.0,
                      due_date=time.time() + 86400)
        at_risk = prediction.at_risk(manager.list())
        assert len(at_risk) == 1
        assert at_risk[0]["invoice_id"].startswith("invoice-")


class TestReceivableEngine:
    def _engine(self):
        return ReceivableEngine()

    def test_facade_delegates(self):
        engine = self._engine()
        invoice = engine.issue_invoice("Cliente A", 1000.0)
        engine.record_payment(invoice.invoice_id, 1000.0)
        assert engine.outstanding_by_customer() == {}
        assert len(engine.at_risk()) == 0

    def test_stats(self):
        engine = self._engine()
        engine.issue_invoice("A", 100.0)
        stats = engine.stats()
        assert stats["invoices"] == 1
        assert stats["outstanding"] == 100.0

    def test_standalone_engine_has_defaults(self):
        engine = ReceivableEngine()
        assert isinstance(engine.invoices, InvoiceManager)
        assert isinstance(engine.collection, Collection)
        assert isinstance(engine.debt, CustomerDebt)
        assert isinstance(engine.prediction, PaymentPrediction)
        assert isinstance(engine.registry, FinanceRegistry)
        assert isinstance(engine.events, FinanceEvents)
