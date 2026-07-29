from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List, Optional

from ..decision_config import DecisionConfig
from ..decision_models import Alert, BusinessArea, Recommendation, RecommendationPriority
from ..decision_security import DecisionSecurityManager
from .action_planner import ActionPlanner
from .priority_manager import PriorityManager
from .optimization import Optimization

logger = logging.getLogger(__name__)


class RecommendationEngine:
    def __init__(self, config: DecisionConfig, security: DecisionSecurityManager):
        self.config = config
        self.security = security
        self.planner: Optional[ActionPlanner] = None
        self.priority: Optional[PriorityManager] = None
        self.optimization: Optional[Optimization] = None
        self._recommendations: List[Recommendation] = []

    async def initialize(self) -> None:
        self.planner = ActionPlanner(self.config)
        self.priority = PriorityManager(self.config)
        self.optimization = Optimization(self.config)
        self._init_defaults()
        logger.info("RecommendationEngine initialized")

    def _init_defaults(self) -> None:
        self._recommendations = [
            Recommendation(
                id=str(uuid.uuid4()), title="Reduzir Compra do Produto X",
                description="Estoque parado aumentando. Reduzir compras em 30%.",
                priority=RecommendationPriority.HIGH, business_area=BusinessArea.SUPPLY_CHAIN,
                roi_estimate=120000.0, effort_hours=40,
            ),
            Recommendation(
                id=str(uuid.uuid4()), title="Criar Promoção para Produto Y",
                description="Liquidação de 20% para girar estoque lento.",
                priority=RecommendationPriority.MEDIUM, business_area=BusinessArea.SALES,
                roi_estimate=80000.0, effort_hours=20,
            ),
            Recommendation(
                id=str(uuid.uuid4()), title="Renegociar Contratos Logísticos",
                description="Aumento de custo logístico. Renegociar para reduzir 10%.",
                priority=RecommendationPriority.CRITICAL, business_area=BusinessArea.OPERATIONS,
                roi_estimate=200000.0, effort_hours=60,
            ),
            Recommendation(
                id=str(uuid.uuid4()), title="Implementar Programa de Retenção",
                description="Churn aumentando. Criar programa de fidelidade.",
                priority=RecommendationPriority.HIGH, business_area=BusinessArea.CUSTOMER,
                roi_estimate=350000.0, effort_hours=200,
            ),
        ]

    async def get_all(self) -> List[Recommendation]:
        return self._recommendations

    async def generate(self, context: Dict[str, Any]) -> List[Recommendation]:
        return self._recommendations

    async def generate_for_alert(self, alert: Alert) -> Optional[Recommendation]:
        rec = Recommendation(
            id=str(uuid.uuid4()),
            title=f"Ação para: {alert.title}",
            description=alert.message,
            priority=RecommendationPriority.HIGH if alert.severity.value in ("critical", "high") else RecommendationPriority.MEDIUM,
        )
        self._recommendations.append(rec)
        return rec

    async def get_by_priority(self, priority: RecommendationPriority) -> List[Recommendation]:
        return [r for r in self._recommendations if r.priority == priority]

    async def get_high_priority(self) -> List[Recommendation]:
        return [r for r in self._recommendations if r.priority in (RecommendationPriority.CRITICAL, RecommendationPriority.HIGH)]

    async def approve(self, rec_id: str, approver: str) -> Optional[Recommendation]:
        for r in self._recommendations:
            if r.id == rec_id:
                r.status = "approved"
                r.approved_by = approver
                return r
        return None

    async def shutdown(self) -> None:
        logger.info("RecommendationEngine shutdown")
