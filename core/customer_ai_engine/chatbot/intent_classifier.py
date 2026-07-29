"""
Intent Classifier - Classify customer message intents using rule-based NLP.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEventBus
from ..customer_config import CustomerConfig

logger = logging.getLogger(__name__)


class IntentClassifier:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._intents = {
            "greeting": {
                "patterns": [r'ol[áa]', r'oi', r'bom dia', r'boa tarde', r'boa noite', r'hey', r'hello', r'hi'],
                "priority": 1,
            },
            "order_status": {
                "patterns": [r'onde est[áa] me(?:u|o)?', r'status do pedido', r'pedido', r'entrega',
                            r'rastre(?:ar|io)', r'cadê', r'cad\^e'],
                "priority": 5,
            },
            "cancel_order": {
                "patterns": [r'cancelar', r'cancelamento', r'quero cancelar', r'desistir'],
                "priority": 8,
            },
            "complaint": {
                "patterns": [r'reclam[aç]', r'problema', r'erro', r'n[ãa]o funcion', r'quebr',
                            r'péssimo', r'horr[ií]vel', r'decepcionad'],
                "priority": 9,
            },
            "pricing": {
                "patterns": [r'pre[çc]o', r'valor', r'quanto custa', r'tabela', r'or[çc]amento',
                            r'custa', r'cobrado'],
                "priority": 4,
            },
            "product_info": {
                "patterns": [r'como funciona', r'o que [ée]', r'especifica[çc]', r'detalhes',
                            r'caracter[ií]stica', r'descri[çc]'],
                "priority": 3,
            },
            "support": {
                "patterns": [r'falar com', r'atendente', r'humano', r'suporte', r'ajuda',
                            r'preciso de', r'pode me ajudar'],
                "priority": 7,
            },
            "farewell": {
                "patterns": [r'tchau', r'até mais', r'obrigad', r'valeu', r'bye', r'at[eé] logo'],
                "priority": 2,
            },
            "negative_feedback": {
                "patterns": [r'n[ãa]o gostei', r'péssimo', r'horr[ií]vel', r'ruim', r'insatisfeit'],
                "priority": 9,
            },
            "payment": {
                "patterns": [r'pagamento', r'boleto', r'cart[ãa]o', r'pix', r'fatura', r'parcel'],
                "priority": 6,
            },
        }

    def classify(self, text: str) -> str:
        text_lower = text.lower().strip()
        best_intent = "unknown"
        best_priority = 0
        for intent_name, config in self._intents.items():
            for pattern in config["patterns"]:
                if re.search(pattern, text_lower):
                    if config["priority"] > best_priority:
                        best_intent = intent_name
                        best_priority = config["priority"]
                    break
        return best_intent

    def get_all_intents(self, text: str) -> Dict[str, float]:
        text_lower = text.lower().strip()
        scores = {}
        for intent_name, config in self._intents.items():
            match_count = 0
            for pattern in config["patterns"]:
                if re.search(pattern, text_lower):
                    match_count += 1
            if match_count > 0:
                scores[intent_name] = match_count / len(config["patterns"])
        return dict(sorted(scores.items(), key=lambda x: -x[1]))

    def add_intent(self, name: str, patterns: List[str], priority: int) -> None:
        self._intents[name] = {"patterns": patterns, "priority": priority}
