from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..decision_config import DecisionConfig
from ..decision_models import BusinessArea, KPI, KpiGroup

logger = logging.getLogger(__name__)

DEFAULT_KPIS = [
    {"id": "kpi-receita", "name": "Receita Total", "value": 2500000.0, "target": 3000000.0, "unit": "R$", "category": "financeiro", "business_area": BusinessArea.FINANCIAL},
    {"id": "kpi-lucro", "name": "Lucro Líquido", "value": 480000.0, "target": 600000.0, "unit": "R$", "category": "financeiro", "business_area": BusinessArea.FINANCIAL},
    {"id": "kpi-margem", "name": "Margem Operacional", "value": 19.2, "target": 25.0, "unit": "%", "category": "financeiro", "business_area": BusinessArea.FINANCIAL},
    {"id": "kpi-clientes", "name": "Clientes Ativos", "value": 35000.0, "target": 40000.0, "unit": "count", "category": "vendas", "business_area": BusinessArea.SALES},
    {"id": "kpi-nps", "name": "NPS", "value": 72.0, "target": 80.0, "unit": "score", "category": "customer", "business_area": BusinessArea.CUSTOMER},
    {"id": "kpi-churn", "name": "Churn Rate", "value": 3.2, "target": 2.5, "unit": "%", "category": "customer", "business_area": BusinessArea.CUSTOMER},
    {"id": "kpi-produtividade", "name": "Produtividade", "value": 85.0, "target": 90.0, "unit": "%", "category": "operacional", "business_area": BusinessArea.OPERATIONS},
    {"id": "kpi-estoque", "name": "Giro de Estoque", "value": 6.5, "target": 8.0, "unit": "x", "category": "operacional", "business_area": BusinessArea.OPERATIONS},
    {"id": "kpi-sla", "name": "SLA Compliance", "value": 94.0, "target": 98.0, "unit": "%", "category": "operacional", "business_area": BusinessArea.OPERATIONS},
    {"id": "kpi-engajamento", "name": "Engajamento", "value": 72.0, "target": 80.0, "unit": "%", "category": "rh", "business_area": BusinessArea.HR},
]


class KPIManager:
    def __init__(self, config: DecisionConfig):
        self._config = config
        self._kpis: Dict[str, KPI] = {}
        self._groups: Dict[str, KpiGroup] = {}
        self._init_defaults()

    def _init_defaults(self) -> None:
        group_map: Dict[str, KpiGroup] = {
            "financeiro": KpiGroup(id="group-fin", name="Indicadores Financeiros", business_area=BusinessArea.FINANCIAL),
            "vendas": KpiGroup(id="group-sales", name="Indicadores de Vendas", business_area=BusinessArea.SALES),
            "customer": KpiGroup(id="group-cx", name="Indicadores de Clientes", business_area=BusinessArea.CUSTOMER),
            "operacional": KpiGroup(id="group-ops", name="Indicadores Operacionais", business_area=BusinessArea.OPERATIONS),
            "rh": KpiGroup(id="group-hr", name="Indicadores de RH", business_area=BusinessArea.HR),
        }
        for data in DEFAULT_KPIS:
            kpi = KPI(**data)
            kpi.change_percent = ((kpi.value - kpi.target) / kpi.target * 100) if kpi.target else 0
            kpi.status = "good" if kpi.change_percent >= 0 else "attention" if kpi.change_percent > -15 else "bad"
            self._kpis[kpi.id] = kpi
            group = group_map.get(data["category"])
            if group:
                group.kpis.append(kpi)
                group.overall_score = sum(k.value / k.target * 100 for k in group.kpis if k.target) / max(len(group.kpis), 1)
        self._groups = group_map

    def get(self, kpi_id: str) -> Optional[KPI]:
        return self._kpis.get(kpi_id)

    def get_all(self) -> List[KPI]:
        return list(self._kpis.values())

    def get_all_values(self) -> Dict[str, float]:
        return {k.id: k.value for k in self._kpis.values()}

    def update(self, kpi_id: str, value: float) -> Optional[KPI]:
        kpi = self._kpis.get(kpi_id)
        if not kpi:
            return None
        kpi.previous_value = kpi.value
        kpi.value = value
        kpi.change_percent = ((value - kpi.target) / kpi.target * 100) if kpi.target else 0
        kpi.status = "good" if kpi.change_percent >= 0 else "attention" if kpi.change_percent > -15 else "bad"
        kpi.last_updated = datetime.utcnow()
        kpi.history.append(value)
        return kpi

    def get_groups(self) -> List[KpiGroup]:
        return list(self._groups.values())

    def get_by_area(self, area: BusinessArea) -> List[KPI]:
        return [k for k in self._kpis.values() if k.business_area == area]
