"""
Recommendation Engine - Generate personalized product recommendations.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

from ..customer_context import CustomerContext
from ..customer_events import CustomerEventBus
from ..customer_models import Recommendation, ChannelType
from ..customer_config import CustomerConfig

logger = logging.getLogger(__name__)


class RecommendationEngine:
    def __init__(self, config: CustomerConfig, context: CustomerContext, event_bus: CustomerEventBus):
        self.config = config
        self.context = context
        self.event_bus = event_bus
        self._product_catalog = {
            "notebook": {"name": "Notebook Pro", "category": "eletrônicos", "price": 4999.00},
            "smartphone": {"name": "Smartphone X", "category": "eletrônicos", "price": 2999.00},
            "headphone": {"name": "Headphone Bluetooth", "category": "acessórios", "price": 299.00},
            "tablet": {"name": "Tablet 10 Polegadas", "category": "eletrônicos", "price": 1999.00},
            "mouse": {"name": "Mouse Wireless", "category": "acessórios", "price": 89.90},
            "teclado": {"name": "Teclado Mecânico", "category": "acessórios", "price": 249.00},
            "monitor": {"name": "Monitor 27 Polegadas", "category": "eletrônicos", "price": 1599.00},
            "cadeira": {"name": "Cadeira Ergonômica", "category": "móveis", "price": 1299.00},
        }

    def generate(self, customer_id: str, profile: Dict[str, Any]) -> List[Recommendation]:
        recs = []
        viewed_categories = profile.get("viewed_categories", [])
        purchase_history = profile.get("purchase_history", [])
        related = self._find_related(purchase_history)
        for product_key, product in self._product_catalog.items():
            score = 0.5
            if product["category"] in viewed_categories:
                score += 0.3
            if product_key in related:
                score += 0.2
            if score >= 0.6:
                recs.append(Recommendation(
                    id=str(uuid.uuid4()),
                    customer_id=customer_id,
                    product_id=product_key,
                    product_name=product["name"],
                    category=product["category"],
                    score=round(score * 100, 1),
                    reason=self._generate_reason(score, product["category"]),
                ))
        recs.sort(key=lambda r: -r.score)
        return recs[:self.config.sales.recommendation_limit]

    def _find_related(self, purchase_history: List[str]) -> List[str]:
        related_map = {
            "notebook": ["mouse", "teclado", "monitor"],
            "smartphone": ["headphone"],
            "tablet": ["teclado"],
        }
        related = []
        for item in purchase_history:
            related.extend(related_map.get(item, []))
        return list(set(related))

    def _generate_reason(self, score: float, category: str) -> str:
        if score >= 0.8:
            return f"Baseado no seu interesse em {category}"
        elif score >= 0.6:
            return f"Recomendado para você"
        return "Produtos relacionados"
