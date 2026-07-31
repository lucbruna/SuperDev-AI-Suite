"""BI Factory — Factory for creating BI components."""

from typing import Any

from .bi_models import KPI, AnalysisType, DataSource, Decision, DecisionType, Insight, MetricType, Prediction


class BIFactory:
    def __init__(self):
        self._templates: dict[str, dict[str, Any]] = {
            "revenue_kpi": {"name": "Revenue", "metric_type": MetricType.CURRENCY, "target": 1000000},
            "conversion_kpi": {"name": "Conversion Rate", "metric_type": MetricType.PERCENTAGE, "target": 5.0},
            "churn_kpi": {"name": "Churn Rate", "metric_type": MetricType.PERCENTAGE, "target": 2.0},
            "nps_kpi": {"name": "NPS Score", "metric_type": MetricType.COUNTER, "target": 50},
        }

    def create_kpi(self, name: str, target: float, metric_type: MetricType = MetricType.RATIO, **kwargs) -> KPI:
        return KPI(name=name, target=target, metric_type=metric_type, **kwargs)

    def create_kpi_from_template(self, template_name: str, **overrides) -> KPI:
        template = self._templates.get(template_name, {})
        params = {**template, **overrides}
        return KPI(**params)

    def create_insight(
        self, title: str, description: str, analysis_type: AnalysisType = AnalysisType.DESCRIPTIVE, **kwargs
    ) -> Insight:
        return Insight(title=title, description=description, analysis_type=analysis_type, **kwargs)

    def create_prediction(
        self, target_metric: str, predicted_value: float, horizon: str = "30d", **kwargs
    ) -> Prediction:
        return Prediction(target_metric=target_metric, predicted_value=predicted_value, horizon=horizon, **kwargs)

    def create_decision(
        self, title: str, options: list[dict[str, Any]], decision_type: DecisionType = DecisionType.STRATEGIC, **kwargs
    ) -> Decision:
        return Decision(title=title, options=options, decision_type=decision_type, **kwargs)

    def create_source(self, name: str, source_type: str = "database", **kwargs) -> DataSource:
        from .bi_models import DataSourceType

        try:
            st = DataSourceType(source_type)
        except ValueError:
            st = DataSourceType.DATABASE
        return DataSource(name=name, source_type=st, **kwargs)

    def register_template(self, name: str, template: dict[str, Any]) -> None:
        self._templates[name] = template

    def get_template(self, name: str) -> dict[str, Any] | None:
        return self._templates.get(name)

    def list_templates(self) -> list[str]:
        return list(self._templates.keys())
