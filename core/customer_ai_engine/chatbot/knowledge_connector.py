"""
Knowledge Connector - Connect to knowledge base for accurate answers.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEventBus
from ..customer_config import CustomerConfig

logger = logging.getLogger(__name__)


class KnowledgeConnector:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._knowledge_base: Dict[str, str] = {
            "horario_funcionamento": "Nosso atendimento funciona de segunda a sexta, das 8h às 18h.",
            "prazo_entrega": "O prazo de entrega padrão é de 5 a 10 dias úteis.",
            "troca_devolucao": "Aceitamos trocas e devoluções em até 30 dias após o recebimento.",
            "formas_pagamento": "Aceitamos cartão de crédito, débito, boleto bancário e PIX.",
            "frete_gratis": "Oferecemos frete grátis para compras acima de R$ 200,00.",
        }

    def search(self, query: str) -> Optional[str]:
        query_lower = query.lower()
        best_match = None
        best_score = 0
        for key, answer in self._knowledge_base.items():
            score = 0
            keywords = key.split("_")
            for kw in keywords:
                if kw in query_lower:
                    score += 1
            if score > best_score:
                best_score = score
                best_match = answer
        return best_match

    def add_knowledge(self, topic: str, answer: str) -> None:
        self._knowledge_base[topic] = answer

    def search_by_category(self, category: str) -> List[Dict[str, str]]:
        results = []
        for key, answer in self._knowledge_base.items():
            if category in key:
                results.append({"topic": key, "answer": answer})
        return results

    def get_all_topics(self) -> List[str]:
        return list(self._knowledge_base.keys())
