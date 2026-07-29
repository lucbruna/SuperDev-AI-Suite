from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..decision_config import DecisionConfig
from ..decision_models import BusinessArea, Pattern

logger = logging.getLogger(__name__)

COMMON_PATTERNS = [
    {"name": "Sazonalidade de Vendas", "description": "Vendas aumentam 25% no último trimestre", "frequency": "annual", "confidence": 0.87, "business_area": BusinessArea.SALES},
    {"name": "Correlação Marketing-Vendas", "description": "Gastos em marketing precedem aumento de vendas em 2 semanas", "frequency": "recurring", "confidence": 0.76, "business_area": BusinessArea.SALES},
    {"name": "Pico de Churn Pós-Contato", "description": "Churn aumenta 40% após 3 tickets sem resolução", "frequency": "recurring", "confidence": 0.82, "business_area": BusinessArea.CUSTOMER},
    {"name": "Eficiência Operacional", "description": "Produtividade máxima entre 9h e 11h", "frequency": "daily", "confidence": 0.91, "business_area": BusinessArea.OPERATIONS},
    {"name": "Tendência de Custos", "description": "Custos logísticos crescem 3% ao mês", "frequency": "monthly", "confidence": 0.79, "business_area": BusinessArea.FINANCIAL},
]


class PatternDetector:
    def __init__(self, config: DecisionConfig):
        self._config = config

    def detect(self) -> List[Pattern]:
        patterns = []
        for data in COMMON_PATTERNS:
            pattern = Pattern(
                id=str(uuid.uuid4()),
                **data,
            )
            patterns.append(pattern)
        return patterns

    def search(self, keyword: str) -> List[Pattern]:
        return [p for p in self.detect() if keyword.lower() in p.name.lower() or keyword.lower() in p.description.lower()]

    def by_area(self, area: BusinessArea) -> List[Pattern]:
        return [p for p in self.detect() if p.business_area == area]
