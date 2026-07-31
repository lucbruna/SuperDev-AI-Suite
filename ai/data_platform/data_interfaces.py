"""Data Platform Interfaces — Protocol interfaces for data platform operations."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from .data_models import DataSource, DataRecord, DataPipeline, DataSchema


class IngestionInterface(ABC):
    @abstractmethod
    def register_source(self, source: DataSource) -> DataSource:
        pass

    @abstractmethod
    def ingest(self, source_id: str, records: List[DataRecord]) -> int:
        pass

    @abstractmethod
    def get_source(self, source_id: str) -> Optional[DataSource]:
        pass


class StorageInterface(ABC):
    @abstractmethod
    def store(self, dataset: str, record: DataRecord) -> bool:
        pass

    @abstractmethod
    def retrieve(self, dataset: str, record_id: str) -> Optional[DataRecord]:
        pass

    @abstractmethod
    def list_datasets(self) -> List[str]:
        pass


class ProcessingInterface(ABC):
    @abstractmethod
    def transform(self, records: List[DataRecord], rules: List[Dict[str, Any]]) -> List[DataRecord]:
        pass

    @abstractmethod
    def aggregate(self, dataset: str, group_by: List[str]) -> List[Dict[str, Any]]:
        pass


class AnalyticsInterface(ABC):
    @abstractmethod
    def query(self, dataset: str, filters: Dict[str, Any]) -> List[DataRecord]:
        pass

    @abstractmethod
    def generate_insights(self, dataset: str) -> List[Dict[str, Any]]:
        pass


class MLInterface(ABC):
    @abstractmethod
    def train(self, dataset: str, model_type: str) -> str:
        pass

    @abstractmethod
    def predict(self, model_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        pass


class GovernanceInterface(ABC):
    @abstractmethod
    def check_access(self, user_id: str, dataset: str) -> bool:
        pass

    @abstractmethod
    def apply_policy(self, dataset: str, policy: Dict[str, Any]) -> bool:
        pass
