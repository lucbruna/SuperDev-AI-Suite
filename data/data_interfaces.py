from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol

from .data_models import (
    DashboardConfig,
    DataBatch,
    DataQualityReport,
    DataRecord,
    ForecastResult,
    KPI,
    MLModel,
    PipelineDefinition,
    PipelineRun,
    Report,
    StarSchema,
    StreamEvent,
)


class IDataSource(ABC):
    """A data source that can be collected from."""

    @abstractmethod
    async def collect(self, config: dict[str, Any] | None = None) -> DataBatch: ...
    @abstractmethod
    def get_name(self) -> str: ...


class IConnector(ABC):
    """Connector abstraction for external systems."""

    @abstractmethod
    async def connect(self, config: dict[str, Any]) -> bool: ...
    @abstractmethod
    async def read(self, query: dict[str, Any] | None = None) -> list[dict[str, Any]]: ...
    @abstractmethod
    async def disconnect(self) -> None: ...


class ITransformer(ABC):
    @abstractmethod
    def transform(self, record: DataRecord) -> DataRecord: ...
    @abstractmethod
    def transform_batch(self, batch: DataBatch) -> DataBatch: ...


class IPipeline(ABC):
    @abstractmethod
    async def execute(self, definition: PipelineDefinition) -> PipelineRun: ...
    @abstractmethod
    async def status(self, run_id: str) -> PipelineRun | None: ...


class IWarehouseStore(ABC):
    @abstractmethod
    async def create_schema(self, schema: StarSchema) -> None: ...
    @abstractmethod
    async def insert(self, table: str, records: list[DataRecord]) -> None: ...
    @abstractmethod
    async def query(self, sql: str) -> list[dict[str, Any]]: ...


class ILakeStore(ABC):
    @abstractmethod
    async def put(self, zone: str, key: str, data: bytes) -> str: ...
    @abstractmethod
    async def get(self, zone: str, key: str) -> bytes | None: ...
    @abstractmethod
    async def list(self, zone: str) -> list[str]: ...


class IEtlExecutor(ABC):
    @abstractmethod
    async def run(self, job_id: str) -> dict[str, Any]: ...
    @abstractmethod
    async def schedule(self, job_id: str, cron: str) -> None: ...


class IAnalytics(ABC):
    @abstractmethod
    async def analyze(self, kind: str, data: list[DataRecord], options: dict[str, Any] | None = None) -> dict[str, Any]: ...


class IBIDashboard(ABC):
    @abstractmethod
    async def render(self, dashboard: DashboardConfig) -> dict[str, Any]: ...
    @abstractmethod
    async def compute_kpi(self, kpi: KPI) -> float: ...


class IMLTrainer(ABC):
    @abstractmethod
    async def train(self, model: MLModel, dataset: str) -> MLModel: ...
    @abstractmethod
    async def predict(self, model: MLModel, features: dict[str, Any]) -> dict[str, Any]: ...


class IForecaster(ABC):
    @abstractmethod
    async def forecast(self, series: list[float], horizon: int, method: str) -> ForecastResult: ...


class IReportRenderer(ABC):
    @abstractmethod
    async def render(self, report: Report) -> str: ...


class IVisualization(ABC):
    @abstractmethod
    async def render_chart(self, chart_type: str, data: dict[str, Any]) -> dict[str, Any]: ...


class IGovernanceEngine(ABC):
    @abstractmethod
    async def evaluate_policy(self, policy_id: str, context: dict[str, Any]) -> bool: ...


class IQualityEngine(ABC):
    @abstractmethod
    async def profile(self, asset_id: str) -> DataQualityReport: ...


class ICatalog(ABC):
    @abstractmethod
    async def search(self, query: str) -> list[dict[str, Any]]: ...


class IStreamProcessor(ABC):
    @abstractmethod
    async def process(self, event: StreamEvent) -> dict[str, Any]: ...


# -- Protocols ---------------------------------------------------------------

class CollectableProtocol(Protocol):
    async def collect(self, config: dict[str, Any] | None = None) -> DataBatch: ...


class TransformableProtocol(Protocol):
    def transform(self, record: DataRecord) -> DataRecord: ...


class PipelineExecutableProtocol(Protocol):
    async def execute(self, definition: PipelineDefinition) -> PipelineRun: ...


class ModelPredictableProtocol(Protocol):
    async def predict(self, features: dict[str, Any]) -> dict[str, Any]: ...


class StreamProcessableProtocol(Protocol):
    async def process(self, event: StreamEvent) -> dict[str, Any]: ...


class ReportRenderableProtocol(Protocol):
    async def render(self, report: Report) -> str: ...


__all__ = [
    "IDataSource", "IConnector", "ITransformer", "IPipeline",
    "IWarehouseStore", "ILakeStore", "IEtlExecutor", "IAnalytics",
    "IBIDashboard", "IMLTrainer", "IForecaster", "IReportRenderer",
    "IVisualization", "IGovernanceEngine", "IQualityEngine", "ICatalog",
    "IStreamProcessor",
    "CollectableProtocol", "TransformableProtocol", "PipelineExecutableProtocol",
    "ModelPredictableProtocol", "StreamProcessableProtocol", "ReportRenderableProtocol",
]
