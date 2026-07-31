"""Registry for the Data Intelligence Engine."""

from __future__ import annotations

from typing import Any


class DataIntelligenceRegistry:
    """Central registry for datasources, models, dashboards and reports."""

    def __init__(self) -> None:
        self._sources: dict[str, Any] = {}
        self._models: dict[str, Any] = {}
        self._dashboards: dict[str, Any] = {}
        self._reports: dict[str, Any] = {}

    # -- datasources -------------------------------------------------------
    def register_source(self, source_id: str, source: Any) -> None:
        self._sources[source_id] = source

    def get_source(self, source_id: str) -> Any | None:
        return self._sources.get(source_id)

    def list_sources(self) -> list[str]:
        return list(self._sources)

    def remove_source(self, source_id: str) -> bool:
        return self._sources.pop(source_id, None) is not None

    # -- models ------------------------------------------------------------
    def register_model(self, model_id: str, model: Any) -> None:
        self._models[model_id] = model

    def get_model(self, model_id: str) -> Any | None:
        return self._models.get(model_id)

    def list_models(self) -> list[str]:
        return list(self._models)

    def remove_model(self, model_id: str) -> bool:
        return self._models.pop(model_id, None) is not None

    # -- dashboards --------------------------------------------------------
    def register_dashboard(self, dashboard_id: str, dashboard: Any) -> None:
        self._dashboards[dashboard_id] = dashboard

    def get_dashboard(self, dashboard_id: str) -> Any | None:
        return self._dashboards.get(dashboard_id)

    def list_dashboards(self) -> list[str]:
        return list(self._dashboards)

    def remove_dashboard(self, dashboard_id: str) -> bool:
        return self._dashboards.pop(dashboard_id, None) is not None

    # -- reports -----------------------------------------------------------
    def register_report(self, report_id: str, report: Any) -> None:
        self._reports[report_id] = report

    def get_report(self, report_id: str) -> Any | None:
        return self._reports.get(report_id)

    def list_reports(self) -> list[str]:
        return list(self._reports)

    def remove_report(self, report_id: str) -> bool:
        return self._reports.pop(report_id, None) is not None

    def stats(self) -> dict[str, int]:
        return {"sources": len(self._sources), "models": len(self._models),
                "dashboards": len(self._dashboards),
                "reports": len(self._reports)}
