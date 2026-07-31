"""Analytics engine."""

import uuid
from datetime import datetime
from typing import Any

from .models import AnalyticsQuery, Dashboard, Insight, InsightType, QueryResult, QueryType


class AnalyticsEngine:
    def __init__(self):
        self._queries: dict[str, AnalyticsQuery] = {}
        self._results: list[QueryResult] = []
        self._insights: list[Insight] = []
        self._dashboards: dict[str, Dashboard] = {}

    def execute_query(self, records: list[dict[str, Any]], query: AnalyticsQuery) -> QueryResult:
        start = datetime.now()
        result_data = list(records)
        if query.filters:
            for key, value in query.filters.items():
                result_data = [r for r in result_data if r.get(key) == value]
        if query.query_type == QueryType.GROUP_BY and query.group_by and query.metrics:
            groups: dict[str, list[dict]] = {}
            for r in result_data:
                key = tuple(str(r.get(g, "")) for g in query.group_by)
                groups.setdefault(key, []).append(r)
            result_data = []
            for key, group in groups.items():
                row = {query.group_by[i]: key[i] for i in range(len(query.group_by))}
                for m in query.metrics:
                    values = [r.get(m, 0) for r in group if isinstance(r.get(m), (int, float))]
                    row[f"sum_{m}"] = sum(values)
                    row[f"avg_{m}"] = sum(values) / len(values) if values else 0
                    row["count"] = len(group)
                result_data.append(row)
        elif query.query_type == QueryType.AGGREGATE and query.metrics:
            row = {}
            for m in query.metrics:
                values = [r.get(m, 0) for r in result_data if isinstance(r.get(m), (int, float))]
                row[f"sum_{m}"] = sum(values)
                row[f"avg_{m}"] = sum(values) / len(values) if values else 0
                row[f"min_{m}"] = min(values) if values else 0
                row[f"max_{m}"] = max(values) if values else 0
            row["count"] = len(result_data)
            result_data = [row]
        result_data = result_data[: query.limit]
        duration = (datetime.now() - start).total_seconds() * 1000
        result = QueryResult(
            result_id=str(uuid.uuid4())[:8],
            query_id=query.query_id,
            rows=result_data,
            row_count=len(result_data),
            execution_ms=duration,
        )
        self._results.append(result)
        self._queries[query.query_id] = query
        return result

    def generate_insights(self, dataset: str, records: list[dict[str, Any]]) -> list[Insight]:
        insights = []
        if records:
            numeric_fields = [k for k, v in records[0].items() if isinstance(v, (int, float))]
            for field_name in numeric_fields:
                values = [r.get(field_name, 0) for r in records if isinstance(r.get(field_name), (int, float))]
                if values:
                    avg = sum(values) / len(values)
                    insight = Insight(
                        insight_id=str(uuid.uuid4())[:8],
                        dataset=dataset,
                        insight_type=InsightType.SUMMARY,
                        title=f"Summary of {field_name}",
                        description=f"Average: {avg:.2f}, Min: {min(values)}, Max: {max(values)}, Count: {len(values)}",
                        data={
                            "field": field_name,
                            "avg": avg,
                            "min": min(values),
                            "max": max(values),
                            "count": len(values),
                        },
                        confidence=0.9,
                    )
                    insights.append(insight)
                    self._insights.append(insight)
        return insights

    def detect_anomalies(
        self, dataset: str, records: list[dict[str, Any]], field_name: str, threshold: float = 2.0
    ) -> list[Insight]:
        values = [r.get(field_name, 0) for r in records if isinstance(r.get(field_name), (int, float))]
        if not values:
            return []
        avg = sum(values) / len(values)
        std = (sum((v - avg) ** 2 for v in values) / len(values)) ** 0.5
        anomalies = []
        for i, r in enumerate(records):
            val = r.get(field_name, 0)
            if isinstance(val, (int, float)) and std > 0 and abs(val - avg) > threshold * std:
                insight = Insight(
                    insight_id=str(uuid.uuid4())[:8],
                    dataset=dataset,
                    insight_type=InsightType.ANOMALY,
                    title=f"Anomaly in {field_name}",
                    description=f"Value {val} is {abs(val - avg) / std:.1f} standard deviations from mean",
                    data={"field": field_name, "value": val, "mean": avg, "std": std, "index": i},
                    confidence=0.85,
                )
                anomalies.append(insight)
                self._insights.append(insight)
        return anomalies

    def create_dashboard(self, dashboard: Dashboard) -> Dashboard:
        self._dashboards[dashboard.dashboard_id] = dashboard
        return dashboard

    def get_dashboard(self, dashboard_id: str) -> Dashboard | None:
        return self._dashboards.get(dashboard_id)

    def get_insights(self, dataset: str | None = None) -> list[Insight]:
        if dataset:
            return [i for i in self._insights if i.dataset == dataset]
        return list(self._insights)

    def get_stats(self) -> dict:
        return {
            "queries": len(self._queries),
            "results": len(self._results),
            "insights": len(self._insights),
            "dashboards": len(self._dashboards),
        }
