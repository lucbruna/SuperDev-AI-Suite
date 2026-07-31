"""Data Platform Interfaces — Protocol interfaces for data platform operations."""

from abc import ABC, abstractmethod
from typing import Any

from .data_models import DataRecord, DataSource


class IngestionInterface(ABC):
    @abstractmethod
    def register_source(self, source: DataSource) -> DataSource:
        pass

    @abstractmethod
    def ingest(self, source_id: str, records: list[DataRecord]) -> int:
        pass

    @abstractmethod
    def get_source(self, source_id: str) -> DataSource | None:
        pass


class StorageInterface(ABC):
    @abstractmethod
    def store(self, dataset: str, record: DataRecord) -> bool:
        pass

    @abstractmethod
    def retrieve(self, dataset: str, record_id: str) -> DataRecord | None:
        pass

    @abstractmethod
    def list_datasets(self) -> list[str]:
        pass


class ProcessingInterface(ABC):
    @abstractmethod
    def transform(self, records: list[DataRecord], rules: list[dict[str, Any]]) -> list[DataRecord]:
        pass

    @abstractmethod
    def aggregate(self, dataset: str, group_by: list[str]) -> list[dict[str, Any]]:
        pass


class AnalyticsInterface(ABC):
    @abstractmethod
    def query(self, dataset: str, filters: dict[str, Any]) -> list[DataRecord]:
        pass

    @abstractmethod
    def generate_insights(self, dataset: str) -> list[dict[str, Any]]:
        pass


class MLInterface(ABC):
    @abstractmethod
    def train(self, dataset: str, model_type: str) -> str:
        pass

    @abstractmethod
    def predict(self, model_id: str, input_data: dict[str, Any]) -> dict[str, Any]:
        pass


class GovernanceInterface(ABC):
    @abstractmethod
    def check_access(self, user_id: str, dataset: str) -> bool:
        pass

    @abstractmethod
    def apply_policy(self, dataset: str, policy: dict[str, Any]) -> bool:
        pass
