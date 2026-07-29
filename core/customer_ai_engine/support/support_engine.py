"""
Support Engine - Core support intelligence coordination.

Manages tickets, classifies problems, recommends solutions, handles escalation.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEvent, CustomerEventBus, EventType
from ..customer_models import Ticket, TicketPriority, TicketStatus
from ..customer_config import CustomerConfig
from .ticket_manager import TicketManager
from .problem_classifier import ProblemClassifier
from .solution_recommender import SolutionRecommender
from .escalation import EscalationManager

logger = logging.getLogger(__name__)


class SupportEngine:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self.tickets: Optional[TicketManager] = None
        self.classifier: Optional[ProblemClassifier] = None
        self.solutions: Optional[SolutionRecommender] = None
        self.escalation: Optional[EscalationManager] = None

    async def initialize(self) -> None:
        self.tickets = TicketManager(self.config, self.context, self.event_bus)
        self.classifier = ProblemClassifier(self.config, self.context, self.event_bus)
        self.solutions = SolutionRecommender(self.config, self.context, self.event_bus)
        self.escalation = EscalationManager(self.config, self.context, self.event_bus)
        logger.info("SupportEngine initialized")

    async def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        return self.tickets.get(ticket_id)

    async def create_ticket(self, customer_id: str, subject: str, description: str) -> Ticket:
        ticket = self.tickets.create(customer_id, subject, description)
        await self.event_bus.publish(CustomerEvent(
            event_type=EventType.TICKET_CREATED,
            payload={"ticket_id": ticket.id, "customer_id": customer_id},
        ))
        return ticket

    async def resolve_ticket(self, ticket_id: str, resolution: str) -> Ticket:
        ticket = self.tickets.resolve(ticket_id, resolution)
        if ticket:
            await self.event_bus.publish(CustomerEvent(
                event_type=EventType.TICKET_RESOLVED,
                payload={"ticket_id": ticket_id},
            ))
        return ticket

    async def escalate(self, payload: Dict[str, Any]) -> None:
        ticket_id = payload.get("ticket_id")
        if ticket_id:
            self.escalation.escalate(ticket_id)

    async def handle_escalation(self, payload: Dict[str, Any]) -> None:
        ticket_id = payload.get("ticket_id")
        if ticket_id:
            self.escalacion.escalate(ticket_id)

    async def shutdown(self) -> None:
        logger.info("SupportEngine shutdown")
