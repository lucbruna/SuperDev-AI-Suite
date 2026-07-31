"""Tax calculation for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

import time
from typing import Any

from finance_intelligence.finance_events import (FinanceEventType,
                                                 FinanceEvents)
from finance_intelligence.finance_metrics import FinanceMetrics
from finance_intelligence.finance_models import (FiscalRegime, TaxRecord,
                                                 Transaction,
                                                 TransactionType)
from finance_intelligence.finance_protocols import new_id, round_money
from finance_intelligence.finance_registry import FinanceRegistry
from finance_intelligence.taxation.tax_rules import TaxRules


class TaxCalculator:
    """Compute tax obligations for transactions."""

    def __init__(self, registry: FinanceRegistry,
                 events: FinanceEvents,
                 metrics: FinanceMetrics,
                 rules: TaxRules | None = None) -> None:
        self.registry = registry
        self.events = events
        self.metrics = metrics
        self.rules = rules or TaxRules()
        self._records: dict[str, TaxRecord] = {}

    def calculate(self, transaction: Transaction,
                  period: str = "") -> TaxRecord:
        tax = "SIMPLES" if self.rules.regime == FiscalRegime.SIMPLES_NACIONAL \
            else "PIS"
        base = transaction.amount if transaction.kind in (
            TransactionType.REVENUE, TransactionType.RECEIPT) else 0.0
        rate = self.rules.rate(tax)
        amount = round_money(base * rate)
        record = TaxRecord(
            tax_id=new_id("tax"), kind=tax, amount=amount,
            period=period, base=base, rate=rate,
            regime=self.rules.regime, created_at=time.time())
        self._records[record.tax_id] = record
        self.metrics.increment("fi.taxes.calculated")
        self.events.publish(FinanceEventType.TAX_CALCULATED,
                            {"tax_id": record.tax_id, "kind": tax,
                             "amount": amount})
        return record

    def calculate_all(self, period: str = "") -> list[TaxRecord]:
        records = [self.calculate(transaction, period)
                   for transaction in self.registry.list_transactions()]
        return records

    def total(self, period: str = "") -> float:
        records = [record for record in self._records.values()
                   if not period or record.period == period]
        return round_money(sum(record.amount for record in records))

    def list(self) -> list[TaxRecord]:
        return list(self._records.values())
