"""Tests for the accounting subsystem (Volume 35, Fase 2)."""

from __future__ import annotations

from finance_intelligence.accounting import AccountingEngine
from finance_intelligence.accounting.journal_entries import (
    JournalEntryManager)
from finance_intelligence.finance_events import (FinanceEventType,
                                                 FinanceEvents)
from finance_intelligence.finance_models import (Account, AccountType,
                                                 Transaction,
                                                 TransactionStatus,
                                                 TransactionType)
from finance_intelligence.finance_registry import FinanceRegistry


class TestJournalEntries:
    def _engine(self):
        return AccountingEngine()

    def test_sale_entry_balances_accounts(self):
        engine = self._engine()
        caixa = Account(account_id="acc-caixa", name="Caixa",
                        account_type=AccountType.ASSET)
        vendas = Account(account_id="acc-vendas", name="Vendas",
                         account_type=AccountType.REVENUE)
        engine.registry.register_account(caixa)
        engine.registry.register_account(vendas)
        entry = engine.journal.create(
            "venda à vista", debits=[(caixa.account_id, 100.0)],
            credits=[(vendas.account_id, 100.0)], reference="NOTA-1")
        assert entry is not None
        assert entry.is_balanced()
        assert caixa.balance == 100.0
        assert vendas.balance == -100.0

    def test_unbalanced_entry_rejected(self):
        engine = self._engine()
        caixa = Account(account_id="a1", name="Caixa",
                        account_type=AccountType.ASSET)
        engine.registry.register_account(caixa)
        entry = engine.journal.create(
            "erro", debits=[(caixa.account_id, 100.0)],
            credits=[(caixa.account_id, 90.0)])
        assert entry is None

    def test_approve_reject(self):
        engine = self._engine()
        caixa = Account(account_id="a1", name="Caixa",
                        account_type=AccountType.ASSET)
        engine.registry.register_account(caixa)
        entry = engine.journal.create(
            "ok", debits=[(caixa.account_id, 10.0)],
            credits=[(caixa.account_id, 10.0)])
        assert entry is not None
        assert engine.journal.approve(entry.entry_id, "finance")
        assert entry.status == TransactionStatus.APPROVED
        assert not engine.journal.reject(entry.entry_id, "guest")
        assert engine.journal.reject(entry.entry_id, "admin")
        assert entry.status == TransactionStatus.REJECTED

    def test_list_entries(self):
        engine = self._engine()
        caixa = Account(account_id="a1", name="Caixa",
                        account_type=AccountType.ASSET)
        engine.registry.register_account(caixa)
        engine.journal.create("e1", debits=[(caixa.account_id, 5.0)],
                              credits=[(caixa.account_id, 5.0)])
        assert len(engine.journal.list()) == 1


class TestLedger:
    def test_trial_balance(self):
        engine = AccountingEngine()
        engine.registry.register_account(
            Account(account_id="a1", name="Caixa",
                    account_type=AccountType.ASSET, balance=500.0))
        engine.registry.register_account(
            Account(account_id="a2", name="Vendas",
                    account_type=AccountType.REVENUE, balance=-500.0))
        trial = engine.ledger.trial_balance()
        assert trial["total_debits"] == 500.0
        assert trial["total_credits"] == 500.0
        assert trial["balanced"] is True

    def test_open_ledger(self):
        engine = AccountingEngine()
        engine.registry.register_account(
            Account(account_id="a1", name="Caixa",
                    account_type=AccountType.ASSET))
        result = engine.ledger.open_ledger("a1", 1000.0)
        assert result["status"] == "opened"
        assert engine.ledger.get_balance("a1") == 1000.0

    def test_close_period(self):
        engine = AccountingEngine()
        engine.registry.register_account(
            Account(account_id="a1", name="Caixa",
                    account_type=AccountType.ASSET))
        report = engine.ledger.close_period()
        assert report["period_closed"] is True
        assert report["account_count"] == 1


class TestAccountingRules:
    def test_double_entry(self):
        from finance_intelligence.finance_models import JournalEntry
        engine = AccountingEngine()
        entry = JournalEntry(
            entry_id="e1", description="x",
            debits=[("a", 10.0)], credits=[("b", 10.0)])
        assert engine.rules.is_double_entry(entry)

    def test_valid_account_type(self):
        engine = AccountingEngine()
        asset = Account(account_id="a", name="Caixa",
                        account_type=AccountType.ASSET)
        revenue = Account(account_id="r", name="Vendas",
                          account_type=AccountType.REVENUE)
        # any registered account may be debited or credited
        assert engine.rules.valid_account_type(asset, is_debit=True)
        assert engine.rules.valid_account_type(asset, is_debit=False)
        assert engine.rules.valid_account_type(revenue, is_debit=True)
        assert engine.rules.valid_account_type(revenue, is_debit=False)

    def test_normal_balance_side(self):
        engine = AccountingEngine()
        asset = Account(account_id="a", name="Caixa",
                        account_type=AccountType.ASSET)
        revenue = Account(account_id="r", name="Vendas",
                          account_type=AccountType.REVENUE)
        assert engine.rules.normal_balance_side(asset) == "debit"
        assert engine.rules.normal_balance_side(revenue) == "credit"

    def test_validate_entry_flags_errors(self):
        from finance_intelligence.finance_models import JournalEntry
        engine = AccountingEngine()
        engine.registry.register_account(
            Account(account_id="a1", name="Caixa",
                    account_type=AccountType.ASSET))
        entry = JournalEntry(
            entry_id="e1", description="bad",
            debits=[("a1", 10.0)], credits=[("revenue-1", 10.0)])
        errors = engine.rules.validate_entry(entry)
        assert any("not found" in error for error in errors)


class TestTransactionProcessor:
    def test_process_expense(self):
        engine = AccountingEngine()
        caixa = Account(account_id="caixa", name="Caixa",
                        account_type=AccountType.ASSET, balance=1000.0)
        despesa = Account(account_id="despesa", name="Insumos",
                          account_type=AccountType.EXPENSE)
        engine.registry.register_account(caixa)
        engine.registry.register_account(despesa)
        transaction = Transaction(
            transaction_id="t1", kind=TransactionType.EXPENSE,
            amount=250.0, description="compra")
        result = engine.processor.process(transaction)
        assert result["status"] == "processed"
        assert caixa.balance == 750.0
        assert despesa.balance == 250.0

    def test_process_revenue(self):
        engine = AccountingEngine()
        caixa = Account(account_id="caixa", name="Caixa",
                        account_type=AccountType.ASSET, balance=0.0)
        vendas = Account(account_id="vendas", name="Vendas",
                         account_type=AccountType.REVENUE)
        engine.registry.register_account(caixa)
        engine.registry.register_account(vendas)
        transaction = Transaction(
            transaction_id="t2", kind=TransactionType.REVENUE, amount=500.0)
        result = engine.processor.process(transaction)
        assert result["status"] == "processed"
        assert caixa.balance == 500.0

    def test_process_requires_cash_account(self):
        engine = AccountingEngine()
        transaction = Transaction(
            transaction_id="t3", kind=TransactionType.REVENUE, amount=10.0)
        result = engine.processor.process(transaction)
        assert result["status"] == "error"


class TestReconciliation:
    def test_matched(self):
        engine = AccountingEngine()
        engine.registry.register_account(
            Account(account_id="a1", name="Caixa",
                    account_type=AccountType.ASSET, balance=100.0))
        result = engine.reconciliation.reconcile("a1", 100.0)
        assert result["status"] == "matched"

    def test_difference_publishes_event(self):
        engine = AccountingEngine()
        engine.registry.register_account(
            Account(account_id="a1", name="Caixa",
                    account_type=AccountType.ASSET, balance=100.0))
        fired = []
        engine.events.on(FinanceEventType.ANOMALY_DETECTED,
                         lambda payload: fired.append(payload))
        result = engine.reconciliation.reconcile("a1", 120.0)
        assert result["status"] == "difference"
        assert result["difference"] == 20.0
        assert len(fired) == 1

    def test_scan_all(self):
        engine = AccountingEngine()
        engine.registry.register_account(
            Account(account_id="a1", name="Caixa",
                    account_type=AccountType.ASSET, balance=100.0))
        differences = engine.reconciliation.scan_all({"a1": 100.0})
        assert differences == []


class TestAccountingEngine:
    def test_facade_delegates(self):
        engine = AccountingEngine()
        caixa = Account(account_id="a1", name="Caixa",
                        account_type=AccountType.ASSET)
        engine.registry.register_account(caixa)
        entry = engine.create_entry("x", debits=[(caixa.account_id, 1.0)],
                                    credits=[(caixa.account_id, 1.0)])
        assert entry is not None
        assert engine.trial_balance()["balanced"] is True

    def test_stats(self):
        engine = AccountingEngine()
        assert "ledger" in engine.stats()
        assert engine.stats()["entries"] == 0

    def test_standalone_engine_has_defaults(self):
        engine = AccountingEngine()
        assert isinstance(engine.registry, FinanceRegistry)
        assert isinstance(engine.events, FinanceEvents)
        assert isinstance(engine.journal, JournalEntryManager)
