"""
Retention Manager - Predict and prevent customer churn.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEvent, CustomerEventBus, EventType
from ..customer_config import CustomerConfig

logger = logging.getLogger(__name__)


class RetentionManager:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._at_risk: Dict[str, datetime] = {}
        self._inactive_days_threshold = 90

    def mark_at_risk(self, customer_id: str) -> None:
        self._at_risk[customer_id] = datetime.utcnow()
        logger.info(f"Customer {customer_id} marked at risk")

    def is_at_risk(self, customer_id: str) -> bool:
        return customer_id in self._at_risk

    def check_inactive(self, last_purchase: datetime) -> bool:
        return (datetime.utcnow() - last_purchase).days > self._inactive_days_threshold

    def get_retention_rate(self, total_customers: int, lost_customers: int) -> float:
        if total_customers == 0:
            return 0.0
        return ((total_customers - lost_customers) / total_customers) * 100

    def get_at_risk_customers(self) -> List[str]:
        return list(self._at_risk.keys())

    def remove_from_risk(self, customer_id: str) -> None:
        self._at_risk.pop(customer_id, None)
