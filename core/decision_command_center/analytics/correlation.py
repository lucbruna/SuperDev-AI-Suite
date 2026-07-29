from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

from ..decision_config import DecisionConfig
from ..decision_models import BusinessArea, Correlation

logger = logging.getLogger(__name__)


DISCOVERED_CORRELATIONS = [
    {"variable_a": "Gastos Marketing", "variable_b": "Receita", "coefficient": 0.82, "strength": "strong", "direction": "positive", "business_area": BusinessArea.SALES},
    {"variable_a": "Tickets Suporte", "variable_b": "Churn", "coefficient": 0.71, "strength": "strong", "direction": "positive", "business_area": BusinessArea.CUSTOMER},
    {"variable_a": "Treinamento Equipe", "variable_b": "Produtividade", "coefficient": 0.65, "strength": "moderate", "direction": "positive", "business_area": BusinessArea.HR},
    {"variable_a": "Temperatura", "variable_b": "Vendas Sorvete", "coefficient": 0.78, "strength": "strong", "direction": "positive", "business_area": BusinessArea.OPERATIONS},
    {"variable_a": "Investimento TI", "variable_b": "Eficiência", "coefficient": 0.59, "strength": "moderate", "direction": "positive", "business_area": BusinessArea.IT},
]


class CorrelationAnalyzer:
    def __init__(self, config: DecisionConfig):
        self._config = config

    def analyze(self) -> List[Dict[str, Any]]:
        results = []
        for data in DISCOVERED_CORRELATIONS:
            corr = Correlation(id=str(uuid.uuid4()), **data)
            results.append({
                "id": corr.id,
                "variables": f"{corr.variable_a} x {corr.variable_b}",
                "coefficient": corr.coefficient,
                "strength": corr.strength,
                "direction": corr.direction,
                "description": f"{corr.variable_a} e {corr.variable_b} têm correlação {corr.strength} {corr.direction}",
            })
        return results

    def find(self, variable: str) -> List[Dict[str, Any]]:
        return [
            r for r in self.analyze()
            if variable.lower() in r["variables"].lower()
        ]

    def get_strong(self, min_coefficient: float = 0.7) -> List[Dict[str, Any]]:
        return [r for r in self.analyze() if r["coefficient"] >= min_coefficient]
