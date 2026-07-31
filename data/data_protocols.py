from __future__ import annotations

from typing import Any, Protocol

from .data_models import DataBatch, DataRecord, ForecastResult, MLModel, StreamEvent


class DataSourceProtocol(Protocol):
    async def collect(self, config: dict[str, Any] | None = None) -> DataBatch: ...


class RecordSourceProtocol(Protocol):
    def get_records(self) -> list[DataRecord]: ...


class TransformProtocol(Protocol):
    def transform(self, record: DataRecord) -> DataRecord: ...


class CleanProtocol(Protocol):
    def clean(self, record: DataRecord) -> DataRecord: ...


class NormalizeProtocol(Protocol):
    def normalize(self, record: DataRecord) -> DataRecord: ...


class EnrichProtocol(Protocol):
    def enrich(self, record: DataRecord) -> DataRecord: ...


class TrainableModelProtocol(Protocol):
    async def train(self, dataset: str) -> MLModel: ...


class PredictableProtocol(Protocol):
    async def predict(self, features: dict[str, Any]) -> dict[str, Any]: ...


class ForecasterProtocol(Protocol):
    async def forecast(self, series: list[float], horizon: int) -> ForecastResult: ...


class StreamHandlerProtocol(Protocol):
    async def handle(self, event: StreamEvent) -> dict[str, Any]: ...


class QualityReportProtocol(Protocol):
    def report(self) -> dict[str, Any]: ...


__all__ = [
    "DataSourceProtocol", "RecordSourceProtocol", "TransformProtocol",
    "CleanProtocol", "NormalizeProtocol", "EnrichProtocol",
    "TrainableModelProtocol", "PredictableProtocol", "ForecasterProtocol",
    "StreamHandlerProtocol", "QualityReportProtocol",
]
