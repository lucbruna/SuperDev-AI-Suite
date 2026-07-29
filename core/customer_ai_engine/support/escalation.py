"""
Escalation Manager - Handle ticket escalation based on priority and SLA.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEvent, CustomerEventBus, EventType
from ..customer_models import Ticket, TicketPriority, TicketStatus
from ..customer_config import CustomerConfig

logger = logging.getLogger(__name__)


class EscalationManager:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._escalation_levels = {0: "first_line", 1: "second_line", 2: "specialist"}

    def escalate(self, ticket_id: str, level: int = 0) -> Dict[str, Any]:
        result = {
            "ticket_id": ticket_id,
            "escalation_level": self._escalation_levels.get(level, "first_line"),
            "escalated_at": datetime.utcnow().isoformat(),
            "status": "escalated",
        }
        logger.info(f"Ticket {ticket_id} escalated to {result['escalation_level']}")
        return result

    def check_sla_breach(self, ticket: Ticket) -> bool:
        if ticket.status in (TicketStatus.RESOLVED, TicketStatus.CLOSED):
            return False
        sla_hours = {
            TicketPriority.CRITICAL: self.config.support.sla_hours_critical,
            TicketPriority.HIGH: self.config.support.sla_hours_high,
            TicketPriority.MEDIUM: self.config.support.sla_hours_medium,
            TicketPriority.LOW: self.config.support.sla_hours_low,
        }.get(ticket.priority, 72)
        elapsed = (datetime.utcnow() - ticket.created_at).total_seconds() / 3600
        return elapsed > sla_hours

    def auto_escalate(self, ticket: Ticket) -> Optional[Dict[str, Any]]:
        if self.check_sla_breach(ticket):
            return self.escalate(ticket.id)
        return None
