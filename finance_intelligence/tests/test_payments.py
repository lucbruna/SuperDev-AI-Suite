"""Tests for the payments subsystem (Volume 35, Fase 3)."""

from __future__ import annotations

import time

from finance_intelligence.finance_events import (FinanceEventType,
                                                 FinanceEvents)
from finance_intelligence.finance_metrics import FinanceMetrics
from finance_intelligence.finance_models import (PaymentMethod,
                                                 PaymentStatus, RiskLevel)
from finance_intelligence.finance_registry import FinanceRegistry
from finance_intelligence.payments import (ApprovalFlow, FraudDetection,
                                           PaymentEngine, PaymentGateway,
                                           PaymentScheduler)


class TestPaymentScheduler:
    def test_schedule(self):
        scheduler = PaymentScheduler(FinanceEvents(), FinanceMetrics())
        payment = scheduler.schedule(
            1200.0, PaymentMethod.PIX, "Fornecedor", due_date=time.time())
        assert payment.payment_id.startswith("payment-")
        assert payment.status == PaymentStatus.SCHEDULED
        assert len(scheduler.list()) == 1

    def test_due_between(self):
        scheduler = PaymentScheduler(FinanceEvents(), FinanceMetrics())
        scheduler.schedule(100.0, due_date=10.0)
        scheduler.schedule(200.0, due_date=20.0)
        scheduler.schedule(300.0, due_date=30.0)
        due = scheduler.due_between(15.0, 25.0)
        assert len(due) == 1
        assert due[0].amount == 200.0

    def test_cancel(self):
        scheduler = PaymentScheduler(FinanceEvents(), FinanceMetrics())
        payment = scheduler.schedule(100.0)
        assert scheduler.cancel(payment.payment_id)
        assert payment.status == PaymentStatus.CANCELLED


class TestApprovalFlow:
    def _flow(self):
        return ApprovalFlow(FinanceEvents(), FinanceMetrics())

    def test_requires_approval_by_amount(self):
        flow = self._flow()
        scheduler = PaymentScheduler(FinanceEvents(), FinanceMetrics())
        big = scheduler.schedule(100000.0)
        small = scheduler.schedule(10.0)
        assert flow.requires_approval(big)
        assert not flow.requires_approval(small)

    def test_request_and_approve(self):
        flow = self._flow()
        scheduler = PaymentScheduler(FinanceEvents(), FinanceMetrics())
        payment = scheduler.schedule(100000.0)
        assert flow.request_approval(payment)
        assert payment.status == PaymentStatus.APPROVAL_REQUIRED
        assert not flow.approve(payment, "guest")
        assert flow.approve(payment, "finance")
        assert payment.status == PaymentStatus.APPROVED

    def test_reject(self):
        flow = self._flow()
        scheduler = PaymentScheduler(FinanceEvents(), FinanceMetrics())
        payment = scheduler.schedule(100000.0)
        flow.request_approval(payment)
        assert flow.reject(payment, "admin")
        assert payment.status == PaymentStatus.CANCELLED


class TestPaymentGateway:
    def test_execute_requires_approval(self):
        gateway = PaymentGateway(FinanceEvents(), FinanceMetrics())
        scheduler = PaymentScheduler(FinanceEvents(), FinanceMetrics())
        payment = scheduler.schedule(100.0)
        result = gateway.execute(payment)
        assert result["status"] == "not_approved"

    def test_execute_approved(self):
        gateway = PaymentGateway(FinanceEvents(), FinanceMetrics())
        scheduler = PaymentScheduler(FinanceEvents(), FinanceMetrics())
        payment = scheduler.schedule(100.0)
        payment.status = PaymentStatus.APPROVED
        result = gateway.execute(payment)
        assert result["status"] == "executed"
        assert payment.status == PaymentStatus.EXECUTED
        assert len(gateway.history()) == 1

    def test_fail(self):
        gateway = PaymentGateway(FinanceEvents(), FinanceMetrics())
        scheduler = PaymentScheduler(FinanceEvents(), FinanceMetrics())
        payment = scheduler.schedule(100.0)
        result = gateway.fail(payment, "insufficient funds")
        assert result["status"] == "failed"
        assert payment.status == PaymentStatus.FAILED


class TestFraudDetection:
    def _detector(self):
        return FraudDetection(FinanceEvents(), FinanceMetrics())

    def test_high_amount_flagged(self):
        detector = self._detector()
        scheduler = PaymentScheduler(FinanceEvents(), FinanceMetrics())
        payment = scheduler.schedule(50000.0, counterparty="X")
        result = detector.analyze(payment)
        assert result["flagged"] is True
        assert result["score"] >= 0.3

    def test_high_risk_flagged(self):
        detector = self._detector()
        scheduler = PaymentScheduler(FinanceEvents(), FinanceMetrics())
        payment = scheduler.schedule(
            100.0, counterparty="X", risk_level=RiskLevel.CRITICAL)
        result = detector.analyze(payment)
        assert result["flagged"] is True
        assert any("risk" in reason for reason in result["reasons"])

    def test_benign_not_flagged(self):
        detector = self._detector()
        scheduler = PaymentScheduler(FinanceEvents(), FinanceMetrics())
        payment = scheduler.schedule(50.0, counterparty="Cliente Confiável")
        result = detector.analyze(payment)
        assert result["flagged"] is False

    def test_publishes_event(self):
        events = FinanceEvents()
        fired = []
        events.on(FinanceEventType.FRAUD_DETECTED,
                  lambda payload: fired.append(payload))
        detector = FraudDetection(events, FinanceMetrics())
        scheduler = PaymentScheduler(events, FinanceMetrics())
        payment = scheduler.schedule(50000.0, counterparty="X")
        detector.analyze(payment)
        assert len(fired) == 1


class TestPaymentEngine:
    def _engine(self):
        return PaymentEngine()

    def test_schedule_auto_approval_flow(self):
        engine = self._engine()
        big = engine.schedule_payment(100000.0, counterparty="X")
        assert big.status == PaymentStatus.APPROVAL_REQUIRED
        small = engine.schedule_payment(100.0, counterparty="Y")
        assert small.status == PaymentStatus.SCHEDULED

    def test_full_flow(self):
        engine = self._engine()
        payment = engine.schedule_payment(100.0, counterparty="Fornecedor")
        assert engine.approvals.request_approval(payment)
        assert engine.approve(payment.payment_id, "admin")
        result = engine.execute(payment.payment_id)
        assert result["status"] == "executed"
        assert payment.status == PaymentStatus.EXECUTED

    def test_execute_blocks_fraud(self):
        engine = self._engine()
        payment = engine.schedule_payment(
            50000.0, counterparty="Desconhecido",
            risk_level=RiskLevel.HIGH)
        result = engine.execute(payment.payment_id)
        assert result["status"] == "blocked"
        assert result["fraud"]["flagged"] is True

    def test_stats(self):
        engine = self._engine()
        engine.schedule_payment(100.0, counterparty="X")
        stats = engine.stats()
        assert stats["scheduled"] == 1

    def test_standalone_engine_has_defaults(self):
        engine = PaymentEngine()
        assert isinstance(engine.scheduler, PaymentScheduler)
        assert isinstance(engine.approvals, ApprovalFlow)
        assert isinstance(engine.gateway, PaymentGateway)
        assert isinstance(engine.fraud, FraudDetection)
        assert isinstance(engine.registry, FinanceRegistry)
        assert isinstance(engine.events, FinanceEvents)
