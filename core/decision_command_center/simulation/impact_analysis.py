from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

from ..decision_config import DecisionConfig

logger = logging.getLogger(__name__)


class ImpactAnalysis:
    def __init__(self, config: DecisionConfig):
        self._config = config

    def analyze(self, change: str, value: float) -> Dict[str, Any]:
        multipliers = {
            "receita": {"custo": 0.6, "lucro": 0.4, "equipe": 0.1},
            "custo": {"receita": -0.3, "lucro": -0.7, "preco": 0.2},
            "preco": {"demanda": -0.5, "receita": 0.3, "margem": 0.8},
            "funcionarios": {"produtividade": 0.3, "custo": 0.8, "receita": 0.4},
        }
        impacts = {}
        if change in multipliers:
            for target, multiplier in multipliers[change].items():
                impacts[f"impacto_{target}"] = round(value * multiplier, 2)
        return {
            "id": str(uuid.uuid4()),
            "change": change,
            "value": value,
            "direct_impacts": impacts,
            "ripple_effects": ["Médio prazo: 3-6 meses para estabilização"],
            "confidence": 0.78,
        }

    def compare_impacts(self, changes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [self.analyze(c["change"], c["value"]) for c in changes]
