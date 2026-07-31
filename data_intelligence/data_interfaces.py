"""Abstract interfaces for the Data Intelligence Engine."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Iterable


class DataConnector(ABC):
    """Connects to a source and produces raw records."""

    @abstractmethod
    def fetch(self, source: Any) -> Iterable[dict[str, Any]]:
        """Returns raw records from the given source."""


class DataSink(ABC):
    """Consumes processed records (warehouse, lake, stream)."""

    @abstractmethod
    def write(self, records: Iterable[dict[str, Any]],
              destination: Any) -> dict[str, Any]:
        """Persists records and returns a write summary."""


class AnalyticsProvider(ABC):
    """Performs analytics computations."""

    @abstractmethod
    def compute(self, metric: str,
                data: list[dict[str, Any]]) -> dict[str, Any]:
        """Computes a metric over the given records."""


class ModelProvider(ABC):
    """Trains and evaluates machine learning models."""

    @abstractmethod
    def train(self, dataset: list[dict[str, Any]], params: dict[str, Any]) -> Any:
        """Trains a model over the dataset."""

    @abstractmethod
    def predict(self, model: Any, features: dict[str, Any]) -> Any:
        """Predicts using the given model."""


class ReportGenerator(ABC):
    """Generates reports from analytics results."""

    @abstractmethod
    def generate(self, report_id: str, data: Any) -> dict[str, Any]:
        """Produces a report dict."""
