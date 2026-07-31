from __future__ import annotations

from typing import Any

from .data_models import (
    DashboardConfig,
    EtlJob,
    ForecastResult,
    KPI,
    MLModel,
    PipelineDefinition,
    Report,
    StarSchema,
)


class DataRegistry:
    """Registry for the Data & Analytics Engine components."""

    def __init__(self) -> None:
        self._sources: dict[str, Any] = {}
        self._connectors: dict[str, Any] = {}
        self._transformers: dict[str, Any] = {}
        self._pipelines: dict[str, PipelineDefinition] = {}
        self._etl_jobs: dict[str, EtlJob] = {}
        self._schemas: dict[str, StarSchema] = {}
        self._models: dict[str, MLModel] = {}
        self._forecasts: dict[str, ForecastResult] = {}
        self._reports: dict[str, Report] = {}
        self._dashboards: dict[str, DashboardConfig] = {}
        self._kpis: dict[str, KPI] = {}
        self._policies: dict[str, Any] = {}
        self._assets: dict[str, Any] = {}

    # -- sources -------------------------------------------------------------

    def register_source(self, name: str, source: Any) -> None:
        self._sources[name] = source

    def get_source(self, name: str) -> Any:
        return self._sources.get(name)

    def list_sources(self) -> dict[str, Any]:
        return dict(self._sources)

    # -- connectors ----------------------------------------------------------

    def register_connector(self, name: str, connector: Any) -> None:
        self._connectors[name] = connector

    def get_connector(self, name: str) -> Any:
        return self._connectors.get(name)

    def list_connectors(self) -> dict[str, Any]:
        return dict(self._connectors)

    # -- transformers --------------------------------------------------------

    def register_transformer(self, name: str, transformer: Any) -> None:
        self._transformers[name] = transformer

    def get_transformer(self, name: str) -> Any:
        return self._transformers.get(name)

    def list_transformers(self) -> dict[str, Any]:
        return dict(self._transformers)

    # -- pipelines -----------------------------------------------------------

    def register_pipeline(self, pipeline: PipelineDefinition) -> None:
        self._pipelines[pipeline.pipeline_id] = pipeline

    def get_pipeline(self, pipeline_id: str) -> PipelineDefinition | None:
        return self._pipelines.get(pipeline_id)

    def list_pipelines(self) -> dict[str, PipelineDefinition]:
        return dict(self._pipelines)

    # -- etl -----------------------------------------------------------------

    def register_etl_job(self, job: EtlJob) -> None:
        self._etl_jobs[job.job_id] = job

    def get_etl_job(self, job_id: str) -> EtlJob | None:
        return self._etl_jobs.get(job_id)

    def list_etl_jobs(self) -> dict[str, EtlJob]:
        return dict(self._etl_jobs)

    # -- schemas -------------------------------------------------------------

    def register_schema(self, schema: StarSchema) -> None:
        self._schemas[schema.name] = schema

    def get_schema(self, name: str) -> StarSchema | None:
        return self._schemas.get(name)

    def list_schemas(self) -> dict[str, StarSchema]:
        return dict(self._schemas)

    # -- models --------------------------------------------------------------

    def register_model(self, model: MLModel) -> None:
        self._models[model.model_id] = model

    def get_model(self, model_id: str) -> MLModel | None:
        return self._models.get(model_id)

    def list_models(self) -> dict[str, MLModel]:
        return dict(self._models)

    # -- forecasts -----------------------------------------------------------

    def register_forecast(self, forecast: ForecastResult) -> None:
        self._forecasts[forecast.forecast_id] = forecast

    def get_forecast(self, forecast_id: str) -> ForecastResult | None:
        return self._forecasts.get(forecast_id)

    # -- reports & dashboards ------------------------------------------------

    def register_report(self, report: Report) -> None:
        self._reports[report.report_id] = report

    def get_report(self, report_id: str) -> Report | None:
        return self._reports.get(report_id)

    def list_reports(self) -> dict[str, Report]:
        return dict(self._reports)

    def register_dashboard(self, dashboard: DashboardConfig) -> None:
        self._dashboards[dashboard.dashboard_id] = dashboard

    def get_dashboard(self, dashboard_id: str) -> DashboardConfig | None:
        return self._dashboards.get(dashboard_id)

    def list_dashboards(self) -> dict[str, DashboardConfig]:
        return dict(self._dashboards)

    # -- KPIs ----------------------------------------------------------------

    def register_kpi(self, kpi: KPI) -> None:
        self._kpis[kpi.kpi_id] = kpi

    def get_kpi(self, kpi_id: str) -> KPI | None:
        return self._kpis.get(kpi_id)

    def list_kpis(self) -> dict[str, KPI]:
        return dict(self._kpis)

    # -- governance ----------------------------------------------------------

    def register_policy(self, policy: Any) -> None:
        self._policies[policy.policy_id] = policy

    def get_policy(self, policy_id: str) -> Any:
        return self._policies.get(policy_id)

    def list_policies(self) -> dict[str, Any]:
        return dict(self._policies)

    # -- assets --------------------------------------------------------------

    def register_asset(self, asset: Any) -> None:
        self._assets[asset.asset_id] = asset

    def get_asset(self, asset_id: str) -> Any:
        return self._assets.get(asset_id)

    def list_assets(self) -> dict[str, Any]:
        return dict(self._assets)

    @property
    def size(self) -> int:
        return (
            len(self._sources)
            + len(self._connectors)
            + len(self._transformers)
            + len(self._pipelines)
            + len(self._etl_jobs)
            + len(self._schemas)
            + len(self._models)
            + len(self._reports)
            + len(self._dashboards)
            + len(self._kpis)
            + len(self._policies)
            + len(self._assets)
        )


__all__ = ["DataRegistry"]
