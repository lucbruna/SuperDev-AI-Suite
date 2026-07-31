"""Interfaces for the Finance Intelligence Engine (Volume 35)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from finance_intelligence.finance_models import (Account, Budget, Forecast,
                                                 Invoice, JournalEntry,
                                                 Payment, TaxRecord,
                                                 Transaction)


class Ledger(ABC):
    """Posting and querying double-entry journal entries."""

    @abstractmethod
    def post(self, entry: JournalEntry) -> bool: ...


class TransactionProcessor(ABC):
    @abstractmethod
    def process(self, transaction: Transaction) -> dict[str, Any]: ...


class PaymentGateway(ABC):
    @abstractmethod
    def execute(self, payment: Payment) -> dict[str, Any]: ...


class TaxCalculator(ABC):
    @abstractmethod
    def calculate(self, transaction: Transaction) -> TaxRecord: ...


class Forecaster(ABC):
    @abstractmethod
    def forecast(self, horizon: str) -> Forecast: ...


class BudgetController(ABC):
    @abstractmethod
    def monitor(self, budget: Budget) -> dict[str, Any]: ...


class InvoiceIssuer(ABC):
    @abstractmethod
    def issue(self, invoice: Invoice) -> Invoice: ...


class AnomalyDetector(ABC):
    @abstractmethod
    def scan(self) -> list[dict[str, Any]]: ...


class ComplianceChecker(ABC):
    @abstractmethod
    def check(self, target: str) -> bool: ...


class AccountStore(ABC):
    @abstractmethod
    def save(self, account: Account) -> bool: ...
