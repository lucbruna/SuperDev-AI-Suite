"""
Financial Events - Event-driven communication for financial systems.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class EventType(Enum):
    CASH_POSITION_UPDATED = "cash.position_updated"
    CASH_LOW = "cash.low"
    CASH_CRITICAL = "cash.critical"
    CASH_SURPLUS = "cash.surplus"
    CASH_FORECAST_UPDATED = "cash.forecast_updated"

    TRANSACTION_POSTED = "accounting.transaction_posted"
    TRANSACTION_CLASSIFIED = "accounting.transaction_classified"
    ACCOUNT_RECONCILED = "accounting.account_reconciled"
    STATEMENT_GENERATED = "accounting.statement_generated"

    BUDGET_CREATED = "budget.created"
    BUDGET_APPROVED = "budget.approved"
    BUDGET_DEVIATION = "budget.deviation_detected"
    BUDGET_EXCEEDED = "budget.exceeded"

    PAYMENT_SCHEDULED = "treasury.payment_scheduled"
    PAYMENT_EXECUTED = "treasury.payment_executed"
    PAYMENT_FAILED = "treasury.payment_failed"
    RECEIVABLE_RECORDED = "treasury.receivable_recorded"
    RECEIVABLE_COLLECTED = "treasury.receivable_collected"

    FORECAST_REVENUE = "forecast.revenue_updated"
    FORECAST_EXPENSE = "forecast.expense_updated"
    FORECAST_PROFITABILITY = "forecast.profitability_changed"
    FORECAST_SCENARIO = "forecast.scenario_run"

    INVESTMENT_OPPORTUNITY = "investment.opportunity_identified"
    INVESTMENT_ANALYZED = "investment.analyzed"
    INVESTMENT_APPROVED = "investment.approved"
    INVESTMENT_REJECTED = "investment.rejected"

    RISK_ASSESSMENT_UPDATED = "risk.assessment_updated"
    RISK_THRESHOLD_EXCEEDED = "risk.threshold_exceeded"
    FRAUD_SUSPECTED = "risk.fraud_suspected"
    CREDIT_SCORE_CHANGED = "risk.credit_score_changed"

    ANOMALY_DETECTED = "audit.anomaly_detected"
    COMPLIANCE_ISSUE = "audit.compliance_issue"
    AUDIT_COMPLETED = "audit.completed"

    FINANCIAL_HEALTH_CHANGED = "financial.health_changed"
    FINANCIAL_ALERT = "financial.alert"


@dataclass
class FinancialEvent:
    event_type: EventType
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = ""
    correlation_id: Optional[str] = None
    priority: int = 0


EventHandler = Union[Callable[[FinancialEvent], None], Callable[[FinancialEvent], Awaitable[None]]]


class FinancialEventBus:
    def __init__(self):
        self._handlers: Dict[EventType, List[EventHandler]] = {}
        self._global_handlers: List[EventHandler] = []
        self._event_history: List[FinancialEvent] = []
        self._max_history = 1000
        self._event_counts: Dict[EventType, int] = {}
        self._queue: asyncio.Queue = asyncio.Queue()
        self._processor_task: Optional[asyncio.Task] = None

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def subscribe_global(self, handler: EventHandler) -> None:
        self._global_handlers.append(handler)

    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> bool:
        if event_type in self._handlers and handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)
            return True
        return False

    async def publish(self, event: FinancialEvent) -> None:
        await self._queue.put(event)
        self._event_counts[event.event_type] = self._event_counts.get(event.event_type, 0) + 1

    async def publish_nowait(self, event: FinancialEvent) -> None:
        await self._process_event(event)

    async def start_processor(self) -> None:
        if self._processor_task is not None:
            return
        self._processor_task = asyncio.create_task(self._event_processor_loop())

    async def stop_processor(self) -> None:
        if self._processor_task:
            self._processor_task.cancel()
            try: await self._processor_task
            except asyncio.CancelledError: pass
            self._processor_task = None

    async def _event_processor_loop(self) -> None:
        while True:
            try:
                event = await self._queue.get()
                await self._process_event(event)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Event processor error: {e}")

    async def _process_event(self, event: FinancialEvent) -> None:
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)
        handlers = list(self._handlers.get(event.event_type, []))
        handlers.extend(self._global_handlers)
        for handler in handlers:
            try:
                result = handler(event)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.error(f"Handler error for {event.event_type}: {e}")

    def get_history(self, event_type: Optional[EventType] = None, limit: int = 50) -> List[FinancialEvent]:
        if event_type:
            return [e for e in self._event_history if e.event_type == event_type][-limit:]
        return self._event_history[-limit:]

    def get_event_count(self, event_type: EventType) -> int:
        return self._event_counts.get(event_type, 0)