from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..decision_config import DecisionConfig

logger = logging.getLogger(__name__)


class StrategySimulator:
    def __init__(self, config: DecisionConfig):
        self._config = config

    def simulate_new_branch(self, params: Dict[str, Any]) -> Dict[str, Any]:
        investment = params.get("investimento_inicial", 500000)
        projected_revenue = params.get("projecao_receita", 20000) * 12
        monthly_cost = investment * 0.02
        annual_cost = monthly_cost * 12
        net_return = projected_revenue - annual_cost
        payback = investment / max(net_return / 12, 1)
        return {
            "scenario": "Nova Filial",
            "investimento": investment,
            "receita_anual_projetada": projected_revenue,
            "custo_anual": annual_cost,
            "retorno_liquido_anual": net_return,
            "payback_meses": round(payback, 1),
            "viabilidade": "viável" if payback < 36 else "inviável",
            "riscos": ["Risco de localização", "Contratação de equipe", "Concorrência local"],
            "recomendacao": "Projeto viável. Retorno estimado em {:.0f} meses.".format(payback),
        }

    def simulate_price_change(self, params: Dict[str, Any]) -> Dict[str, Any]:
        current_price = params.get("preco_atual", 100)
        new_price = params.get("novo_preco", 120)
        elasticity = params.get("elasticidade", 1.5)
        qty_change_pct = -elasticity * (new_price - current_price) / current_price * 100
        new_revenue = params.get("current_quantity", 1000) * (1 + qty_change_pct / 100) * new_price
        old_revenue = params.get("current_quantity", 1000) * current_price
        return {
            "scenario": "Mudança de Preço",
            "current_price": current_price,
            "new_price": new_price,
            "demand_change_pct": round(qty_change_pct, 1),
            "old_revenue": old_revenue,
            "new_revenue": round(new_revenue, 2),
            "revenue_impact": round(new_revenue - old_revenue, 2),
            "recommendation": "Aumentar preço" if new_revenue > old_revenue else "Manter preço atual",
        }

    def simulate_hiring(self, params: Dict[str, Any]) -> Dict[str, Any]:
        quantity = params.get("quantidade", 5)
        salary = params.get("salario_medio", 5000)
        monthly_cost = quantity * salary * 1.7
        annual_cost = monthly_cost * 12
        revenue_impact = params.get("impacto_receita", monthly_cost * 3)
        return {
            "scenario": "Contratação",
            "quantidade": quantity,
            "custo_mensal_total": monthly_cost,
            "custo_anual_total": annual_cost,
            "receita_adicional_estimada": revenue_impact,
            "roi_anual": round((revenue_impact - annual_cost) / annual_cost * 100, 1),
            "tempo_retorno_meses": round(annual_cost / max(revenue_impact / 12, 1), 1),
            "recommendation": "Contratação recomendada" if revenue_impact > annual_cost else "Avaliar necessidade",
        }

    def generic_simulation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "scenario": params.get("name", "Custom Scenario"),
            "parameters": params,
            "projected_impact": {k: v for k, v in params.items() if isinstance(v, (int, float))},
            "confidence": 0.75,
            "risks": ["Incertezas de mercado", "Premissas não validadas"],
            "recommendation": "Validar premissas antes de decidir",
        }
