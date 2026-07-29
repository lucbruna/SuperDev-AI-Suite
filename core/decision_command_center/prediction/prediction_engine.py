from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ..decision_config import DecisionConfig
from ..decision_models import Prediction, RevenueForecast
from ..decision_security import DecisionSecurityManager
from .revenue_prediction import RevenuePrediction
from .demand_prediction import DemandPrediction
from .risk_prediction import RiskPrediction

logger = logging.getLogger(__name__)


class PredictionEngine:
    def __init__(self, config: DecisionConfig, security: DecisionSecurityManager):
        self.config = config
        self.security = security
        self.revenue: Optional[RevenuePrediction] = None
        self.demand: Optional[DemandPrediction] = None
        self.risk: Optional[RiskPrediction] = None

    async def initialize(self) -> None:
        self.revenue = RevenuePrediction(self.config)
        self.demand = DemandPrediction(self.config)
        self.risk = RiskPrediction(self.config)
        logger.info("PredictionEngine initialized")

    async def get_all_predictions(self) -> List[Prediction]:
        predictions = []
        predictions.append(self.revenue.predict_next_quarter())
        predictions.append(self.demand.predict_next_month())
        predictions.append(self.risk.predict_next_period())
        predictions.append(self.revenue.predict_growth())
        return [p for p in predictions if p is not None]

    async def get_revenue_forecast(self) -> RevenueForecast:
        return self.revenue.generate_forecast()

    async def get_demand_forecast(self) -> Dict[str, Any]:
        return self.demand.forecast_all()

    async def get_risk_forecast(self) -> Dict[str, Any]:
        return self.risk.assess_all()

    async def predict(self, metric: str, horizon: str = "30d") -> Prediction:
        if metric == "revenue":
            return self.revenue.predict_next_quarter()
        elif metric == "demand":
            return self.demand.predict_next_month()
        elif metric == "risk":
            return self.risk.predict_next_period()
        return Prediction(id="unknown", metric=metric, current_value=0, predicted_value=0, confidence=0, time_horizon=horizon)

    async def shutdown(self) -> None:
        logger.info("PredictionEngine shutdown")
