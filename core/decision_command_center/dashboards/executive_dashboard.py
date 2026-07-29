from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..decision_config import DecisionConfig
from ..decision_models import Dashboard, DashboardType, Widget, ChartType

logger = logging.getLogger(__name__)


class ExecutiveDashboard:
    def __init__(self, config: DecisionConfig):
        self._config = config

    def build(self) -> Dashboard:
        dash = Dashboard(
            id=str(uuid.uuid4()),
            name="Painel Executivo - Visão Geral",
            dashboard_type=DashboardType.EXECUTIVE,
            owner="ceo",
        )
        dash.widgets = [
            {"id": "kpi-receita", "title": "Receita", "chart_type": "kpi_card"},
            {"id": "kpi-lucro", "title": "Lucro", "chart_type": "kpi_card"},
            {"id": "kpi-clientes", "title": "Clientes Ativos", "chart_type": "kpi_card"},
            {"id": "chart-receita", "title": "Tendência de Receita", "chart_type": "line"},
            {"id": "chart-vendas", "title": "Vendas por Região", "chart_type": "bar"},
            {"id": "chart-riscos", "title": "Indicadores de Risco", "chart_type": "gauge"},
            {"id": "alerts-list", "title": "Alertas Ativos", "chart_type": "table"},
        ]
        return dash

    def get_ceo_view(self) -> Dict[str, Any]:
        return {
            "faturamento_mensal": 2500000.0,
            "lucro_mensal": 480000.0,
            "margem": 19.2,
            "clientes_ativos": 35000,
            "ticket_medio": 285.0,
            "nps": 72,
            "churn": 3.2,
            "riscos_criticos": 0,
            "oportunidades": 5,
            "ultima_atualizacao": datetime.utcnow().isoformat(),
        }

    def get_company_overview(self) -> Dict[str, Any]:
        return {
            "name": "SuperDev Enterprise",
            "segment": "Tecnologia",
            "revenue": {"current": 2500000, "projected": 2875000, "growth": 15.0},
            "costs": {"current": 2020000, "projected": 2181600, "growth": 8.0},
            "profit": {"current": 480000, "projected": 693400, "growth": 44.5},
            "employees": 1250,
            "clients": 35000,
            "health": "good",
        }
