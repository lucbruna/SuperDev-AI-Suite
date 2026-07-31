"""BI Engine — Core engine for business intelligence operations."""
from typing import Dict, Any, Optional, List
from datetime import datetime
from .bi_models import DataSource, DataPoint, KPI, Insight, Prediction, Decision


class BIEngine:
    def __init__(self):
        self._sources: Dict[str, DataSource] = {}
        self._data_points: List[DataPoint] = []
        self._kpis: Dict[str, KPI] = {}
        self._insights: List[Insight] = []
        self._predictions: List[Prediction] = []
        self._decisions: List[Decision] = []

    def register_source(self, source: DataSource) -> str:
        self._sources[source.source_id] = source
        return source.source_id

    def ingest_data(self, points: List[DataPoint]) -> int:
        self._data_points.extend(points)
        return len(points)

    def add_kpi(self, kpi: KPI) -> str:
        self._kpis[kpi.kpi_id] = kpi
        return kpi.kpi_id

    def add_insight(self, insight: Insight) -> str:
        self._insights.append(insight)
        return insight.insight_id

    def add_prediction(self, prediction: Prediction) -> str:
        self._predictions.append(prediction)
        return prediction.prediction_id

    def add_decision(self, decision: Decision) -> str:
        self._decisions.append(decision)
        return decision.decision_id

    def get_kpi(self, kpi_id: str) -> Optional[KPI]:
        return self._kpis.get(kpi_id)

    def get_all_kpis(self) -> List[KPI]:
        return list(self._kpis.values())

    def get_insights(self) -> List[Insight]:
        return list(self._insights)

    def get_predictions(self) -> List[Prediction]:
        return list(self._predictions)

    def get_decisions(self) -> List[Decision]:
        return list(self._decisions)

    def get_stats(self) -> Dict[str, Any]:
        return {
            "sources": len(self._sources),
            "data_points": len(self._data_points),
            "kpis": len(self._kpis),
            "insights": len(self._insights),
            "predictions": len(self._predictions),
            "decisions": len(self._decisions),
        }
