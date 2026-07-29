"""
Ticket Manager - Create, manage, and resolve support tickets.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEventBus
from ..customer_models import Ticket, TicketPriority, TicketStatus
from ..customer_config import CustomerConfig

logger = logging.getLogger(__name__)


class TicketManager:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._tickets: Dict[str, Ticket] = {}

    def create(self, customer_id: str, subject: str, description: str,
               priority: TicketPriority = TicketPriority.MEDIUM) -> Ticket:
        ticket = Ticket(
            id=f"TK-{uuid.uuid4().hex[:8].upper()}",
            customer_id=customer_id,
            subject=subject,
            description=description,
            priority=priority,
            status=TicketStatus.OPEN,
            category=self._auto_categorize(subject),
        )
        self._tickets[ticket.id] = ticket
        logger.info(f"Ticket created: {ticket.id} for {customer_id}")
        return ticket

    def get(self, ticket_id: str) -> Optional[Ticket]:
        return self._tickets.get(ticket_id)

    def update(self, ticket_id: str, updates: Dict[str, Any]) -> Optional[Ticket]:
        ticket = self._tickets.get(ticket_id)
        if not ticket:
            return None
        for key, value in updates.items():
            if hasattr(ticket, key):
                setattr(ticket, key, value)
        return ticket

    def resolve(self, ticket_id: str, resolution: str) -> Optional[Ticket]:
        ticket = self._tickets.get(ticket_id)
        if not ticket:
            return None
        ticket.status = TicketStatus.RESOLVED
        ticket.resolution = resolution
        ticket.resolved_at = datetime.utcnow()
        logger.info(f"Ticket resolved: {ticket_id}")
        return ticket

    def assign(self, ticket_id: str, agent: str) -> Optional[Ticket]:
        ticket = self._tickets.get(ticket_id)
        if not ticket:
            return None
        ticket.assigned_to = agent
        ticket.status = TicketStatus.IN_PROGRESS
        return ticket

    def list_by_customer(self, customer_id: str) -> List[Ticket]:
        return [t for t in self._tickets.values() if t.customer_id == customer_id]

    def list_by_status(self, status: TicketStatus) -> List[Ticket]:
        return [t for t in self._tickets.values() if t.status == status]

    def get_open_count(self) -> int:
        return sum(1 for t in self._tickets.values() if t.status in (TicketStatus.OPEN, TicketStatus.IN_PROGRESS))

    def _auto_categorize(self, subject: str) -> str:
        subject_lower = subject.lower()
        if any(w in subject_lower for w in ["pagamento", "boleto", "fatura", "cobrança"]):
            return "financial"
        if any(w in subject_lower for w in ["entrega", "frete", "prazo", "envio"]):
            return "shipping"
        if any(w in subject_lower for w in ["produto", "defeito", "quebrou", "troca"]):
            return "product_issue"
        if any(w in subject_lower for w in ["cancelar", "cancelamento"]):
            return "cancellation"
        if any(w in subject_lower for w in ["acesso", "login", "senha", "sistema"]):
            return "technical"
        return "general"
