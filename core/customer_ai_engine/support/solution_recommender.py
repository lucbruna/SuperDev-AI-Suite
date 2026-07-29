"""
Solution Recommender - Recommend solutions based on problem patterns.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEventBus
from ..customer_models import Ticket
from ..customer_config import CustomerConfig

logger = logging.getLogger(__name__)


class SolutionRecommender:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._solution_kb = [
            {"patterns": [r'pagamento', r'boleto'], "solution": "Verifique o status do boleto na área do cliente. Boletos vencidos podem ser reemitidos."},
            {"patterns": [r'entrega', r'frete', r'prazo'], "solution": "Consulte o código de rastreamento enviado por e-mail. O prazo padrão é de 5 a 10 dias úteis."},
            {"patterns": [r'cancelar', r'cancelamento'], "solution": "Para cancelar, acesse 'Meus Pedidos' na área do cliente ou confirme seus dados para cancelamento."},
            {"patterns": [r'senha', r'acesso', r'login'], "solution": "Utilize a opção 'Esqueci minha senha' na página de login para redefinir seu acesso."},
            {"patterns": [r'troca', r'devolu', r'defeito'], "solution": "Aceitamos trocas em até 30 dias. Inicie o processo na área do cliente em 'Minhas Compras'."},
        ]

    def recommend(self, ticket: Ticket) -> List[str]:
        text = (ticket.subject + " " + ticket.description).lower()
        solutions = []
        for entry in self._solution_kb:
            for pattern in entry["patterns"]:
                if re.search(pattern, text):
                    solutions.append(entry["solution"])
                    break
        if not solutions:
            solutions.append("Encaminhe o problema para nossa equipe de suporte para análise personalizada.")
        return solutions

    def add_solution(self, patterns: List[str], solution: str) -> None:
        self._solution_kb.append({"patterns": patterns, "solution": solution})
