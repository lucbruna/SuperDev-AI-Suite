from __future__ import annotations

from typing import Any

from .data_config import DataConfig
from .data_context import DataContext
from .data_events import DataEventBus
from .data_logger import DataLogger
from .data_metrics import DataMetrics
from .data_registry import DataRegistry
from .data_runtime import DataRuntime
from .data_security import DataSecurity

from .ingestion.ingestion_engine import IngestionEngine
from .processing.processing_engine import ProcessingEngine
from .pipelines.pipeline_engine import PipelineEngine
from .warehouse.warehouse_engine import WarehouseEngine
from .lake.lake_engine import LakeEngine
from .etl.etl_engine import EtlEngine
from .analytics.analytics_engine import AnalyticsEngine
from .bi.bi_engine import BIEngine
from .machine_learning.ml_engine import MLEngine
from .forecasting.forecasting_engine import ForecastingEngine
from .reporting.report_engine import ReportEngine
from .visualization.visualization_engine import VisualizationEngine
from .governance.governance_engine import GovernanceEngine
from .quality.quality_engine import QualityEngine
from .catalog.catalog_engine import CatalogEngine
from .streaming.streaming_engine import StreamingEngine


class DataEngine:
    """Central orchestrator for the Data & Analytics Engine.

    Owns and coordinates all 16 subsystems:
    ingestion → processing → pipelines → warehouse/lake → etl → analytics →
    bi → machine_learning → forecasting → reporting → visualization →
    governance → quality → catalog → streaming.
    """

    def __init__(self, config: DataConfig | None = None) -> None:
        self._config = config or DataConfig.default()
        self._event_bus = DataEventBus()
        self._logger = DataLogger(name="data-engine")
        self._metrics = DataMetrics()
        self._registry = DataRegistry()
        self._runtime = DataRuntime()
        self._security = DataSecurity()
        self._context = DataContext()
        self._running = False

        # Subsystems
        self.ingestion = IngestionEngine(self)
        self.processing = ProcessingEngine(self)
        self.pipelines = PipelineEngine(self)
        self.warehouse = WarehouseEngine(self)
        self.lake = LakeEngine(self)
        self.etl = EtlEngine(self)
        self.analytics = AnalyticsEngine(self)
        self.bi = BIEngine(self)
        self.machine_learning = MLEngine(self)
        self.forecasting = ForecastingEngine(self)
        self.reporting = ReportEngine(self)
        self.visualization = VisualizationEngine(self)
        self.governance = GovernanceEngine(self)
        self.quality = QualityEngine(self)
        self.catalog = CatalogEngine(self)
        self.streaming = StreamingEngine(self)

    # -- lifecycle -----------------------------------------------------------

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._runtime.start()
        for subsystem in self._subsystems():
            await subsystem.initialize()
        await self._event_bus.emit("data.engine.started", {"config": self._config})
        self._logger.info("DataEngine started")

    async def stop(self) -> None:
        if not self._running:
            return
        for subsystem in self._subsystems():
            await subsystem.shutdown()
        self._running = False
        await self._event_bus.emit("data.engine.stopped", {})
        self._logger.info("DataEngine stopped")

    def _subsystems(self) -> list[Any]:
        return [
            self.ingestion, self.processing, self.pipelines, self.warehouse,
            self.lake, self.etl, self.analytics, self.bi, self.machine_learning,
            self.forecasting, self.reporting, self.visualization, self.governance,
            self.quality, self.catalog, self.streaming,
        ]

    # -- high-level flows ----------------------------------------------------

    async def collect_and_process(self, source: str, config: dict[str, Any] | None = None) -> dict[str, Any]:
        """End-to-end flow: ingest from a source, then process the batch."""
        batch = await self.ingestion.ingest(source, config or {})
        processed = await self.processing.process_batch(batch)
        self._metrics.increment("flows.collect_and_process")
        return {
            "batch_id": processed.batch_id,
            "source": processed.source,
            "records": len(processed.records),
        }

    async def run_pipeline(self, pipeline_id: str) -> dict[str, Any]:
        run = await self.pipelines.run(pipeline_id)
        self._metrics.increment("flows.run_pipeline")
        return {"run_id": run.run_id, "status": run.status.value}

    async def run_etl(self, job_id: str) -> dict[str, Any]:
        result = await self.etl.run_job(job_id)
        self._metrics.increment("flows.run_etl")
        return result

    async def forecast(self, series: list[float], horizon: int = 30) -> dict[str, Any]:
        result = await self.forecasting.forecast(series, horizon=horizon)
        self._metrics.increment("flows.forecast")
        return {
            "forecast_id": result.forecast_id,
            "horizon": result.horizon,
            "values": result.values,
            "confidence": result.confidence,
        }

    async def generate_report(self, title: str, kind: str = "executive") -> dict[str, Any]:
        report = await self.reporting.create_report(title=title, kind=kind)
        self._metrics.increment("flows.generate_report")
        return {"report_id": report.report_id, "title": report.title}

    async def emit_event(self, stream: str, payload: dict[str, Any]) -> dict[str, Any]:
        event = await self.streaming.publish(stream, payload)
        self._metrics.increment("flows.emit_event")
        return {"event_id": event.event_id, "stream": event.stream}

    # -- status --------------------------------------------------------------

    def status(self) -> dict[str, Any]:
        return {
            "running": self._running,
            "subsystems": {
                s.__class__.__name__: s.status()
                for s in self._subsystems()
            },
            "runtime": self._runtime.snapshot(),
            "registry_size": self._registry.size,
            "metrics": self._metrics.snapshot(),
        }

    async def health(self) -> dict[str, Any]:
        return {
            "running": self._running,
            "uptime": self._runtime.uptime,
            "subsystems_initialized": sum(
                1 for s in self._subsystems() if s.status().get("initialized")
            ),
            "config": {
                "ingestion": self._config.ingestion.enabled,
                "processing": self._config.processing.enabled,
                "pipelines": self._config.pipelines.enabled,
                "warehouse": self._config.warehouse.enabled,
                "lake": self._config.lake.enabled,
                "etl": self._config.etl.enabled,
                "analytics": self._config.analytics.enabled,
                "bi": self._config.bi.enabled,
                "machine_learning": self._config.machine_learning.enabled,
                "forecasting": self._config.forecasting.enabled,
                "reporting": self._config.reporting.enabled,
                "visualization": self._config.visualization.enabled,
                "governance": self._config.governance.enabled,
                "quality": self._config.quality.enabled,
                "catalog": self._config.catalog.enabled,
                "streaming": self._config.streaming.enabled,
            },
        }

    # -- accessors -----------------------------------------------------------

    @property
    def config(self) -> DataConfig:
        return self._config

    @property
    def event_bus(self) -> DataEventBus:
        return self._event_bus

    @property
    def logger(self) -> DataLogger:
        return self._logger

    @property
    def metrics(self) -> DataMetrics:
        return self._metrics

    @property
    def registry(self) -> DataRegistry:
        return self._registry

    @property
    def runtime(self) -> DataRuntime:
        return self._runtime

    @property
    def security(self) -> DataSecurity:
        return self._security

    @property
    def context(self) -> DataContext:
        return self._context

    @property
    def is_running(self) -> bool:
        return self._running


__all__ = ["DataEngine"]
