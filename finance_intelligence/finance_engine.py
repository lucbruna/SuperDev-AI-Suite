"""Finance Intelligence Engine facade (Volume 35).

Aggregate facade over the finance subsystems, exposing subsystem engines
lazily via ``engine.accounting_engine`` once attached.
"""

from __future__ import annotations

from typing import Any

from finance_intelligence.finance_config import FinanceConfig
from finance_intelligence.finance_context import FinanceContext
from finance_intelligence.finance_events import FinanceEvents
from finance_intelligence.finance_logger import get_logger
from finance_intelligence.finance_manager import FinanceManager
from finance_intelligence.finance_metrics import FinanceMetrics
from finance_intelligence.finance_models import (Account, AccountType,
                                                 JournalEntry, RiskLevel,
                                                 Transaction,
                                                 TransactionType)
from finance_intelligence.finance_registry import FinanceRegistry
from finance_intelligence.finance_runtime import FinanceRuntime
from finance_intelligence.finance_security import FinanceSecurity


class FinanceEngine:
    """Aggregate facade over the finance subsystems."""

    def __init__(self, config: FinanceConfig | None = None,
                 events: FinanceEvents | None = None,
                 metrics: FinanceMetrics | None = None,
                 registry: FinanceRegistry | None = None,
                 security: FinanceSecurity | None = None,
                 context: FinanceContext | None = None,
                 runtime: FinanceRuntime | None = None) -> None:
        self._log = get_logger()
        self.config = config or FinanceConfig()
        self.events = events or FinanceEvents()
        self.metrics = metrics or FinanceMetrics()
        self.registry = registry or FinanceRegistry()
        self.security = security or FinanceSecurity(
            approval_threshold=self.config.approval_threshold)
        self.context = context or FinanceContext()
        self.runtime = runtime or FinanceRuntime()
        self.manager = FinanceManager(
            registry=self.registry, events=self.events, metrics=self.metrics,
            config=self.config, context=self.context, security=self.security,
            engine=self)
        self._subsystems: dict[str, Any] = {}

    # -- lifecycle ----------------------------------------------------------
    def start(self) -> bool:
        return self.runtime.start()

    def stop(self) -> bool:
        return self.runtime.stop()

    def run(self) -> bool:
        return self.start()

    # -- subsystem attachment ----------------------------------------------
    def attach_subsystem(self, name: str, engine: Any) -> None:
        self._subsystems[name] = engine
        setattr(self, name, engine)
        setattr(self.manager, name, engine)

    def __getattr__(self, name: str) -> Any:
        if name in self._subsystems:
            return self._subsystems[name]
        raise AttributeError(f"no subsystem or attribute '{name}'")

    # -- account facade ------------------------------------------------------
    def create_account(self, name: str,
                       account_type: AccountType = AccountType.ASSET,
                       balance: float = 0.0,
                       currency: str = "") -> Account:
        return self.manager.create_account(name, account_type, balance,
                                           currency)

    def get_account(self, account_id: str) -> Account | None:
        return self.manager.get_account(account_id)

    def list_accounts(self) -> list[Account]:
        return self.manager.list_accounts()

    def remove_account(self, account_id: str) -> bool:
        return self.manager.remove_account(account_id)

    # -- journal facade ------------------------------------------------------
    def post_entry(self, description: str,
                   debits: list[tuple[str, float]],
                   credits: list[tuple[str, float]],
                   reference: str = "") -> JournalEntry | None:
        return self.manager.post_entry(description, debits, credits,
                                       reference)

    # -- transaction facade --------------------------------------------------
    def record_transaction(self, kind: TransactionType, amount: float,
                           counterparty: str = "",
                           risk_level: RiskLevel = RiskLevel.LOW,
                           description: str = "") -> Transaction:
        return self.manager.record_transaction(
            kind, amount, counterparty, risk_level, description)

    def get_transaction(self, transaction_id: str) -> Transaction | None:
        return self.manager.get_transaction(transaction_id)

    def list_transactions(self) -> list[Transaction]:
        return self.manager.list_transactions()

    # -- audit / alert facade ------------------------------------------------
    def record_audit(self, event: str, actor: str = "system",
                     target: str = "",
                     detail: dict[str, Any] | None = None):
        return self.manager.record_audit(event, actor, target, detail)

    def raise_alert(self, level: RiskLevel, message: str,
                    source: str = "core"):
        return self.manager.raise_alert(level, message, source)

    def list_alerts(self):
        return self.manager.list_alerts()

    # -- misc ---------------------------------------------------------------
    def stats(self) -> dict[str, Any]:
        return {
            "manager": self.manager.stats(),
            "subsystems": list(self._subsystems),
            "runtime": self.runtime.state(),
        }
