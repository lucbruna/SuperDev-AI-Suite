"""Analytics engine implementation."""

import uuid
from datetime import datetime
from typing import Any

from .config import AnalyticsConfig
from .interfaces import AnalyticsEngineInterface
from .models import AnalysisRequest, AnalysisResult, DataPoint, Insight, InsightType


class AnalyticsEngine(AnalyticsEngineInterface):
    def __init__(self, config: AnalyticsConfig | None = None):
        self._config = config or AnalyticsConfig()
        self._data_points: list[DataPoint] = []
        self._insights: list[Insight] = []

    async def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        start = datetime.now()
        relevant = self._filter_data(request)
        insights = self._generate_insights(request, relevant)
        summary = self._compute_summary(relevant)
        elapsed = (datetime.now() - start).total_seconds() * 1000
        return AnalysisResult(
            request_id=request.request_id,
            status="completed",
            data_points=relevant,
            insights=insights,
            summary=summary,
            execution_time_ms=elapsed,
        )

    async def ingest_data(self, data_points: list[DataPoint]) -> bool:
        self._data_points.extend(data_points)
        return True

    async def get_insights(self, time_range: tuple | None = None) -> list[Insight]:
        if time_range:
            start, end = time_range
            return [i for i in self._insights if start <= i.created_at <= end]
        return list(self._insights)

    def _filter_data(self, request: AnalysisRequest) -> list[DataPoint]:
        result = self._data_points
        if request.time_range_start:
            result = [d for d in result if d.timestamp >= request.time_range_start]
        if request.time_range_end:
            result = [d for d in result if d.timestamp <= request.time_range_end]
        return result

    def _generate_insights(self, request: AnalysisRequest, data: list[DataPoint]) -> list[Insight]:
        if not data:
            return []
        values = [d.value for d in data]
        avg = sum(values) / len(values)
        insights = []
        if len(values) > 1:
            trend = "increasing" if values[-1] > values[0] else "decreasing"
            insights.append(
                Insight(
                    insight_id=str(uuid.uuid4()),
                    insight_type=InsightType.TREND,
                    title=f"Data trend: {trend}",
                    description=f"Values are {trend} over the period (avg={avg:.2f})",
                    confidence=min(1.0, len(values) / 10),
                    data_points=data[:5],
                )
            )
        std = (sum((v - avg) ** 2 for v in values) / len(values)) ** 0.5
        for d in data:
            if abs(d.value - avg) > 2 * std:
                insights.append(
                    Insight(
                        insight_id=str(uuid.uuid4()),
                        insight_type=InsightType.ANOMALY,
                        title=f"Anomaly detected: {d.value}",
                        description=f"Value {d.value} deviates from mean {avg:.2f} by >2σ",
                        confidence=0.85,
                        data_points=[d],
                    )
                )
        return insights

    def _compute_summary(self, data: list[DataPoint]) -> dict[str, Any]:
        if not data:
            return {"count": 0}
        values = [d.value for d in data]
        return {
            "count": len(values),
            "sum": sum(values),
            "mean": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
        }
