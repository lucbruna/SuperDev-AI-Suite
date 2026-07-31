"""Tests for the Finance Intelligence core (Volume 35, Fase 1)."""

from __future__ import annotations

import pytest

from finance_intelligence import (build_finance_engine, coerce_bool,
                                  coerce_number, new_id, normalize,
                                  round_money, safe_get, tokenize, top_n)
from finance_intelligence.finance_config import FinanceConfig
from finance_intelligence.finance_events import (FinanceEventType,
                                                 FinanceEvents)
from finance_intelligence.finance_models import (Account, AccountStatus,
                                                 AccountType, FiscalRegime,
                                                 InvoiceStatus, JournalEntry,
                                                 PaymentStatus, RiskLevel,
                                                 Transaction,
                                                 TransactionStatus,
                                                 TransactionType)
from finance_intelligence.finance_protocols import now
from finance_intelligence.finance_registry import FinanceRegistry
from finance_intelligence.finance_security import FinanceSecurity


class TestConfig:
    def test_defaults_and_get(self):
        config = FinanceConfig()
        assert config.currency == "BRL"
        assert config.get("approval_threshold") == 50000.0
        assert config.get("missing", 7) == 7

    def test_overrides_and_snapshot(self):
        config = FinanceConfig(currency="USD", custom_opt="x")
        assert config.currency == "USD"
        snapshot = config.snapshot()
        assert snapshot["currency"] == "USD"
        assert snapshot["fiscal_regime"] == "simples_nacional"
        assert "custom_opt" not in snapshot

    def test_fiscal_regime_coercion(self):
        config = FinanceConfig(fiscal_regime="lucro_real")
        assert config.fiscal_regime == FiscalRegime.LUCRO_REAL
        config2 = FinanceConfig(
            fiscal_regime=FiscalRegime.LUCRO_PRESUMIDO)
        assert config2.fiscal_regime == FiscalRegime.LUCRO_PRESUMIDO

    def test_merge(self):
        config = FinanceConfig().merge({"approval_threshold": 1000})
        assert config.approval_threshold == 1000


class TestEvents:
    def test_on_publish_off(self):
        events = FinanceEvents()
        seen = []
        handler = lambda payload: seen.append(payload)  # noqa: E731
        events.on(FinanceEventType.TRANSACTION_RECORDED, handler)
        events.publish(FinanceEventType.TRANSACTION_RECORDED,
                       {"transaction_id": "t1"})
        events.off(FinanceEventType.TRANSACTION_RECORDED, handler)
        events.publish(FinanceEventType.TRANSACTION_RECORDED,
                       {"transaction_id": "t2"})
        assert len(seen) == 1

    def test_once(self):
        events = FinanceEvents()
        seen = []
        events.once(FinanceEventType.INVOICE_ISSUED,
                    lambda payload: seen.append(payload))
        events.publish(FinanceEventType.INVOICE_ISSUED, {})
        events.publish(FinanceEventType.INVOICE_ISSUED, {})
        assert len(seen) == 1

    def test_listener_isolation(self):
        events = FinanceEvents()

        def boom(_payload):
            raise ValueError("boom")

        events.on(FinanceEventType.PAYMENT_FAILED, boom)
        events.publish(FinanceEventType.PAYMENT_FAILED, {})  # no raise


class TestProtocols:
    def test_new_id_prefix(self):
        assert new_id("account").startswith("account-")
        assert new_id("entry").startswith("entry-")

    def test_coerce(self):
        assert coerce_bool("true") is True
        assert coerce_bool("nope") is False
        assert coerce_number("3.5") == 3.5
        assert coerce_number("abc", 1.0) == 1.0

    def test_round_money(self):
        assert round_money(10.005) == 10.01
        assert round_money("9.999") == 10.0
        assert round_money("abc", 0) == 0.0

    def test_text_helpers(self):
        assert normalize("  Conta   Corrente ") == "conta corrente"
        assert tokenize("fluxo de caixa") == ["fluxo", "de", "caixa"]

    def test_safe_get(self):
        data = {"a": {"b": 1}}
        assert safe_get(data, "a.b") == 1
        assert safe_get(data, "a.c", 9) == 9

    def test_top_n(self):
        items = [{"v": 1}, {"v": 5}, {"v": 3}]
        result = top_n(items, key=lambda item: item["v"], limit=2)
        assert [item["v"] for item in result] == [5, 3]


class TestModels:
    def test_account(self):
        account = Account(account_id="acc-1", name="Caixa",
                          account_type=AccountType.ASSET)
        assert account.is_active()
        assert account.can_debit()
        assert not account.can_credit()
        assert account.currency == "BRL"

    def test_revenue_account_credit(self):
        account = Account(account_id="acc-2", name="Vendas",
                          account_type=AccountType.REVENUE)
        assert account.can_credit()
        assert not account.can_debit()

    def test_journal_entry_balance(self):
        entry = JournalEntry(
            entry_id="e-1", description="venda",
            debits=[("caixa", 100.0)], credits=[("vendas", 100.0)])
        assert entry.is_balanced()
        assert entry.debit_total() == 100.0

    def test_journal_entry_unbalanced(self):
        entry = JournalEntry(
            entry_id="e-2", description="erro",
            debits=[("caixa", 100.0)], credits=[("vendas", 90.0)])
        assert not entry.is_balanced()

    def test_risk_rank(self):
        assert RiskLevel.CRITICAL.rank > RiskLevel.LOW.rank

    def test_invoice_outstanding(self):
        from finance_intelligence.finance_models import Invoice
        invoice = Invoice(invoice_id="i-1", customer="Acme",
                          amount=1000.0, paid_amount=400.0)
        assert invoice.outstanding() == 600.0
        assert invoice.status == InvoiceStatus.DRAFT

    def test_transaction_defaults(self):
        transaction = Transaction(transaction_id="t-1",
                                  kind=TransactionType.REVENUE,
                                  amount=50.0)
        assert transaction.status == TransactionStatus.PENDING
        assert transaction.risk_level == RiskLevel.LOW


class TestSecurity:
    def test_permissions(self):
        security = FinanceSecurity()
        assert security.can("a1", "pay", granted=["pay", "read"])
        assert not security.can("a1", "delete")
        security.grant("a1", "delete")
        assert security.can("a1", "delete")

    def test_approval_policy(self):
        security = FinanceSecurity()
        assert not security.requires_approval(1000.0)
        assert security.requires_approval(100000.0)
        assert security.requires_approval(1000.0, RiskLevel.CRITICAL)

    def test_approve_roles(self):
        security = FinanceSecurity()
        assert security.approve("admin")
        assert security.approve("finance")
        assert not security.approve("guest")

    def test_sanitize(self):
        security = FinanceSecurity()
        assert "<script>" not in security.sanitize("<script>alert(1)</script>")
        assert not security.is_safe("<script>alert(1)</script>")


class TestRegistry:
    def test_account_crud(self):
        registry = FinanceRegistry()
        account = Account(account_id="a1", name="Caixa")
        registry.register_account(account)
        assert registry.get_account("a1") is account
        assert registry.count_accounts() == 1
        assert registry.remove_account("a1")
        assert not registry.remove_account("a1")

    def test_alerts(self):
        from finance_intelligence.finance_models import FinancialAlert
        registry = FinanceRegistry()
        alert = FinancialAlert(alert_id="al-1", level=RiskLevel.HIGH,
                               message="risco")
        registry.register_alert(alert)
        assert len(registry.open_alerts()) == 1
        assert registry.resolve_alert("al-1")
        assert len(registry.open_alerts()) == 0

    def test_stats(self):
        registry = FinanceRegistry()
        registry.register_account(Account(account_id="a1", name="Caixa"))
        registry.register_transaction(Transaction(
            transaction_id="t1", kind=TransactionType.EXPENSE, amount=1.0))
        stats = registry.stats()
        assert stats["accounts"] == 1
        assert stats["transactions"] == 1


class TestManagerAndEngine:
    @pytest.fixture
    def engine(self):
        return build_finance_engine()

    def test_account_lifecycle(self, engine):
        account = engine.create_account("Caixa", AccountType.ASSET, 1000.0)
        assert account.account_id.startswith("account-")
        assert engine.get_account(account.account_id) is account
        assert len(engine.list_accounts()) == 1
        assert engine.remove_account(account.account_id)
        assert len(engine.list_accounts()) == 0

    def test_journal_posting(self, engine):
        caixa = engine.create_account("Caixa", AccountType.ASSET)
        vendas = engine.create_account("Vendas", AccountType.REVENUE)
        entry = engine.post_entry(
            "venda à vista",
            debits=[(caixa.account_id, 100.0)],
            credits=[(vendas.account_id, 100.0)],
            reference="NOTA-1")
        assert entry is not None
        assert entry.is_balanced()
        assert engine.get_account(caixa.account_id).balance == 100.0
        assert engine.get_account(vendas.account_id).balance == -100.0

    def test_unbalanced_entry_rejected(self, engine):
        caixa = engine.create_account("Caixa", AccountType.ASSET)
        entry = engine.post_entry(
            "erro",
            debits=[(caixa.account_id, 100.0)],
            credits=[(caixa.account_id, 90.0)])
        assert entry is None

    def test_transaction_flow(self, engine):
        transaction = engine.record_transaction(
            TransactionType.EXPENSE, 2500.0, "Fornecedor LTDA",
            RiskLevel.MEDIUM, "compra de insumos")
        assert transaction.status == TransactionStatus.PENDING
        assert engine.manager.approve_transaction(
            transaction.transaction_id, "finance")
        assert transaction.status == TransactionStatus.APPROVED
        assert not engine.manager.approve_transaction(
            transaction.transaction_id, "guest")

    def test_audit_trail(self, engine):
        audit = engine.record_audit("payment.executed", "admin",
                                    "pay-1", {"amount": 100.0})
        assert audit.audit_id.startswith("audit-")
        assert len(engine.manager.list_audits()) == 1

    def test_alert_flow(self, engine):
        alert = engine.raise_alert(RiskLevel.HIGH, "provável fraude",
                                   "payments")
        assert alert is not None
        assert not alert.resolved
        assert engine.manager.resolve_alert(alert.alert_id)
        assert alert.resolved

    def test_alert_limit(self):
        engine = build_finance_engine({"max_open_alerts": 2})
        engine.raise_alert(RiskLevel.LOW, "a", "s1")
        engine.raise_alert(RiskLevel.LOW, "b", "s1")
        blocked = engine.raise_alert(RiskLevel.LOW, "c", "s1")
        assert blocked is None

    def test_attach_subsystem(self, engine):
        fake = object()
        engine.attach_subsystem("accounting_engine", fake)
        assert engine.accounting_engine is fake
        assert engine.manager.accounting_engine is fake
        assert "accounting_engine" in engine.stats()["subsystems"]

    def test_runtime_lifecycle(self, engine):
        assert engine.start()
        assert not engine.start()
        assert engine.runtime.is_running()
        assert engine.stop()
        assert not engine.stop()

    def test_factory_overrides(self):
        engine = build_finance_engine({"currency": "USD"})
        assert engine.config.currency == "USD"

    def test_stats(self, engine):
        stats = engine.stats()
        assert "manager" in stats
        assert stats["runtime"]["state"] == "stopped"


class TestContext:
    def test_snapshot(self):
        from finance_intelligence.finance_context import FinanceContext
        context = FinanceContext(company="Acme", owner="tom")
        context.set("branch", "main")
        snapshot = context.snapshot()
        assert snapshot["company"] == "Acme"
        assert snapshot["metadata"]["branch"] == "main"
        assert context.get("branch") == "main"
        assert context.get("missing", 0) == 0


class TestInterfaces:
    def test_abstract_binding(self):
        from finance_intelligence.finance_interfaces import (
            AccountStore, AnomalyDetector, BudgetController,
            ComplianceChecker, Forecaster, InvoiceIssuer, Ledger,
            PaymentGateway, TaxCalculator, TransactionProcessor)
        interfaces = [Ledger, TransactionProcessor, PaymentGateway,
                      TaxCalculator, Forecaster, BudgetController,
                      InvoiceIssuer, AnomalyDetector, ComplianceChecker,
                      AccountStore]
        assert all(getattr(interface, "__abstractmethods__")
                   for interface in interfaces)
