"""
Response Generator - Generate contextual responses based on intent.
"""

from __future__ import annotations

import logging
import random
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEventBus
from ..customer_models import Conversation, ChannelType
from ..customer_config import CustomerConfig

logger = logging.getLogger(__name__)


class ResponseGenerator:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._responses = {
            "greeting": [
                "Olá! Como posso ajudar você hoje?",
                "Oi! Em que posso ser útil?",
                "Olá! Bem-vindo ao nosso atendimento. Como posso ajudar?",
            ],
            "order_status": [
                "Vou verificar o status do seu pedido. Um momento...",
                "Deixe-me consultar seu pedido. Por favor, confirme seu CPF ou número do pedido.",
                "Claro! Vou buscar as informações do seu pedido agora.",
            ],
            "cancel_order": [
                "Entendo que deseja cancelar. Vou verificar as condições do seu pedido.",
                "Vou analisar a possibilidade de cancelamento. Um momento, por favor.",
                "Cancelamento solicitado! Preciso de algumas informações para prosseguir.",
            ],
            "complaint": [
                "Sinto muito por isso! Deixe-me encaminhar para nossa equipe de suporte.",
                "Lamento o ocorrido. Vou abrir um chamado prioritário para resolver isso.",
                "Peço desculpas pelo transtorno. Já estou verificando a melhor solução.",
            ],
            "pricing": [
                "Vou consultar nossos preços e condições especiais para você.",
                "Temos diversas opções! Deixe-me buscar as informações de valores.",
                "Claro! Posso enviar nossa tabela de preços atualizada.",
            ],
            "product_info": [
                "Deixe-me buscar as informações detalhadas sobre este produto.",
                "Vou consultar nossas especificações técnicas para você.",
                "Claro! Tenho todas as informações sobre este produto.",
            ],
            "support": [
                "Vou transferir você para um de nossos atendentes especializados.",
                "Um momento, vou encaminhar seu caso para nossa equipe de suporte.",
                "Deixe-me conectar você com um atendente humano.",
            ],
            "farewell": [
                "Obrigado pelo contato! Estamos sempre à disposição.",
                "Foi um prazer ajudar! Volte sempre que precisar.",
                "Até mais! Tenha um ótimo dia!",
            ],
            "negative_feedback": [
                "Sinto muito que não tenha gostado. Vou registrar seu feedback para melhorarmos.",
                "Agradecemos seu feedback sincero. Isso nos ajuda a melhorar!",
                "Lamento sua insatisfação. Vou encaminhar para nossa equipe de qualidade.",
            ],
            "payment": [
                "Vou verificar as informações de pagamento para você.",
                "Claro! Posso ajudar com questões de pagamento, boleto ou parcelamento.",
                "Deixe-me consultar as opções de pagamento disponíveis.",
            ],
            "unknown": [
                "Não entendi completamente. Você pode reformular?",
                "Desculpe, não consegui entender. Pode explicar de outra forma?",
                "Não tenho essa informação ainda. Vou transferir para um atendente.",
            ],
        }

    def generate(self, intent: str, message: str, conversation: Conversation) -> str:
        responses = self._responses.get(intent, self._responses["unknown"])
        return random.choice(responses)

    def add_custom_response(self, intent: str, responses: List[str]) -> None:
        if intent in self._responses:
            self._responses[intent].extend(responses)
        else:
            self._responses[intent] = responses

    def generate_contextual(self, intent: str, context_data: Dict[str, Any]) -> str:
        if intent == "order_status" and "order_id" in context_data:
            return f"Seu pedido #{context_data['order_id']} está {context_data.get('status', 'em processamento')}."
        if intent == "pricing" and "product" in context_data:
            return f"O {context_data['product']} está a partir de R$ {context_data.get('price', 'consultar')}."
        return self.generate(intent, "", Conversation(id="ctx", customer_id="ctx"))
