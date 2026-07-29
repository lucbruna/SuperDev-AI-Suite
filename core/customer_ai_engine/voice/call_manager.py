"""
Call Manager - Manage phone call lifecycle and records.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEventBus
from ..customer_models import CallRecord, SentimentType
from ..customer_config import CustomerConfig

logger = logging.getLogger(__name__)


class CallManager:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._calls: Dict[str, CallRecord] = {}

    def create(self, caller_number: str) -> CallRecord:
        record = CallRecord(
            id=str(uuid.uuid4()),
            customer_id="",
            caller_number=caller_number,
        )
        self._calls[record.id] = record
        logger.info(f"Call created: {record.id} from {caller_number}")
        return record

    def get(self, call_id: str) -> Optional[CallRecord]:
        return self._calls.get(call_id)

    def end(self, call_id: str) -> CallRecord:
        call = self._calls.get(call_id)
        if not call:
            raise ValueError(f"Call not found: {call_id}")
        call.status = "completed"
        return call

    def get_active_calls(self) -> List[CallRecord]:
        return [c for c in self._calls.values() if c.status == "completed"]

    def get_calls_by_customer(self, customer_id: str) -> List[CallRecord]:
        return [c for c in self._calls.values() if c.customer_id == customer_id]
