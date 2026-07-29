from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..decision_config import DecisionConfig

logger = logging.getLogger(__name__)


class RealtimeDashboard:
    def __init__(self, config: DecisionConfig):
        self._config = config
        self._status: Dict[str, str] = {}

    def update_status(self, area: str, status: str) -> None:
        self._status[area] = status

    def get_status(self) -> Dict[str, str]:
        return {
            "financeiro": self._status.get("financeiro", "🟢 Normal"),
            "vendas": self._status.get("vendas", "🟢 Normal"),
            "estoque": self._status.get("estoque", "🟢 Normal"),
            "seguranca": self._status.get("seguranca", "🟢 Protegido"),
            "infraestrutura": self._status.get("infraestrutura", "🟢 Operacional"),
            "operacoes": self._status.get("operacoes", "🟢 Normal"),
            "clientes": self._status.get("clientes", "🟢 Normal"),
            "updated_at": datetime.utcnow().isoformat(),
        }

    def get_company_snapshot(self) -> Dict[str, Any]:
        return {
            "faturamento": "R$ 2.500.000",
            "lucro": "R$ 480.000",
            "clientes_ativos": 35000,
            "riscos": 2,
            "alerts": 0,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def refresh(self) -> None:
        logger.debug("Realtime dashboard refreshed")

    def get_live_indicators(self) -> Dict[str, Any]:
        return {
            "receita_hora": 42500.0,
            "pedidos_hora": 87,
            "tickets_abertos": 23,
            "tempo_medio_atendimento": "4min",
            "satisfacao_agora": 4.3,
        }
