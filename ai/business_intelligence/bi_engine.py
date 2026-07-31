"""BI Engine — Core engine for business intelligence operations."""

from typing import Any

from .bi_models import KPI, DataPoint, DataSource, Decision, Insight, Prediction


class BIEngine:
    def __init__(self):
        self._sources: dict[str, DataSource] = {}
        self._data_points: list[DataPoint] = []
        self._kpis: dict[str, KPI] = {}
        self._insights: list[Insight] = []
        self._predictions: list[Prediction] = []
        self._decisions: list[Decision] = []

    def register_source(self, source: DataSource) -> str:
        self._sources[source.source_id] = source
        return source.source_id

    def ingest_data(self, points: list[DataPoint]) -> int:
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

    def get_kpi(self, kpi_id: str) -> KPI | None:
        return self._kpis.get(kpi_id)

    def get_all_kpis(self) -> list[KPI]:
        return list(self._kpis.values())

    def get_insights(self) -> list[Insight]:
        return list(self._insights)

    def get_predictions(self) -> list[Prediction]:
        return list(self._predictions)

    def get_decisions(self) -> list[Decision]:
        return list(self._decisions)

    def get_stats(self) -> dict[str, Any]:
        return {
            "sources": len(self._sources),
            "data_points": len(self._data_points),
            "kpis": len(self._kpis),
            "insights": len(self._insights),
            "predictions": len(self._predictions),
            "decisions": len(self._decisions),
        }
