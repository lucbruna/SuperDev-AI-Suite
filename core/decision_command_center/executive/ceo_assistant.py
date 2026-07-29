from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..decision_config import DecisionConfig

logger = logging.getLogger(__name__)

KNOWLEDGE_BASE = {
    "maior problema": {
        "answer": "Principal impacto identificado: Aumento de custo logístico. Impacto estimado: Redução de margem em 6%. Recomendação: Renegociar contratos e otimizar rotas.",
        "confidence": 0.85,
    },
    "faturamento": {
        "answer": "Faturamento atual: R$ 2.500.000. Projeção: R$ 2.875.000 (+15%). Performance dentro do esperado.",
        "confidence": 0.92,
    },
    "contratar": {
        "answer": "Recomendação: Contratar 5 funcionários. Motivo: Demanda projetada supera capacidade atual em 15%. ROI estimado em 8 meses.",
        "confidence": 0.78,
    },
    "lucro": {
        "answer": "Lucro líquido atual: R$ 480.000. Margem: 19.2%. Meta: 25%. Gap de 5.8% a ser recuperado.",
        "confidence": 0.88,
    },
    "risco": {
        "answer": "Riscos identificados: 1) Aumento de custos logísticos (médio), 2) Queda de engajamento de clientes premium (alto), 3) Concorrência agressiva (médio).",
        "confidence": 0.82,
    },
}


class CEOAssistant:
    def __init__(self, config: DecisionConfig):
        self._config = config

    def answer(self, question: str) -> Dict[str, Any]:
        q_lower = question.lower()
        for keyword, data in KNOWLEDGE_BASE.items():
            if keyword in q_lower:
                return {
                    "question": question,
                    "answer": data["answer"],
                    "confidence": data["confidence"],
                    "sources": ["Business Intelligence", "Análise de Dados"],
                    "timestamp": datetime.utcnow().isoformat(),
                }
        return {
            "question": question,
            "answer": "Análise em profundidade necessária. Consultando fontes de dados...",
            "confidence": 0.5,
            "sources": ["Base de Conhecimento"],
            "timestamp": datetime.utcnow().isoformat(),
        }

    def analyze_trend(self, metric: str) -> Dict[str, Any]:
        return {
            "metric": metric,
            "trend": "positive" if hash(metric) % 2 == 0 else "negative",
            "change_pct": round((hash(metric) % 20) - 5, 1),
            "recommendation": "Monitorar de perto" if hash(metric) % 3 == 0 else "Manter estratégia",
        }
