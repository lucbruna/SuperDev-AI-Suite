"""
Problem Classifier - Classify support problems by type and priority.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEventBus
from ..customer_models import TicketPriority, Ticket
from ..customer_config import CustomerConfig

logger = logging.getLogger(__name__)


class ProblemClassifier:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._classification_rules = {
            TicketPriority.CRITICAL: [
                r'sistema (?:parou|fora|indispon[ií]vel|caiu)',
                r'falha (?:cr[ií]tica|grave|total)',
                r'perda de dados',
                r'vazamento',
                r'urgente',
                r'emerg[eê]ncia',
            ],
            TicketPriority.HIGH: [
                r'erro (?:de|no) (?:sistema|pagamento|processo)',
                r'n[ãa]o (?:est[áa]|consegue) (?:funcionando|acessar)',
                r'problema (?:grave|s[eé]rio|urgente)',
                r'atraso na entrega',
                r'cobrança indevida',
            ],
            TicketPriority.MEDIUM: [
                r'ajuda com',
                r'como (?:fa[çc]o|posso)',
                r'd[ií]vida',
                r'orienta[çc][ãa]o',
                r'suporte',
                r'informa[çc][ãa]o',
            ],
        }

    def classify(self, ticket: Ticket) -> TicketPriority:
        text = (ticket.subject + " " + ticket.description).lower()
        for priority, patterns in self._classification_rules.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    ticket.priority = priority
                    return priority
        ticket.priority = TicketPriority.LOW
        return TicketPriority.LOW

    def get_category(self, ticket: Ticket) -> str:
        text = (ticket.subject + " " + ticket.description).lower()
        if re.search(r'pagamento|boleto|fatura|cobran', text):
            return "financial"
        if re.search(r'entrega|frete|envio|prazo', text):
            return "shipping"
        if re.search(r'produto|defeito|quebr|troca|devolu', text):
            return "product"
        if re.search(r'cancel', text):
            return "cancellation"
        if re.search(r'acesso|login|senha|sistema|t[eé]cnico', text):
            return "technical"
        return "general"

    def get_sla_hours(self, priority: TicketPriority) -> int:
        sla_map = {
            TicketPriority.CRITICAL: self.config.support.sla_hours_critical,
            TicketPriority.HIGH: self.config.support.sla_hours_high,
            TicketPriority.MEDIUM: self.config.support.sla_hours_medium,
            TicketPriority.LOW: self.config.support.sla_hours_low,
        }
        return sla_map.get(priority, 72)
