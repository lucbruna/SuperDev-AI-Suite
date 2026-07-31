"""Analytics engine interfaces."""
from abc import ABC, abstractmethod
from typing import Any

from .models import AnalysisRequest, AnalysisResult, DataPoint, Insight


class AnalyticsEngineInterface(ABC):
    @abstractmethod
    async def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        pass

    @abstractmethod
    async def ingest_data(self, data_points: list[DataPoint]) -> bool:
        pass

    @abstractmethod
    async def get_insights(self, time_range: tuple | None = None) -> list[Insight]:
        pass


class DataWarehouseInterface(ABC):
    @abstractmethod
    async def query(self, sql: str, params: dict | None = None) -> list[dict]:
        pass

    @abstractmethod
    async def store(self, table: str, records: list[dict]) -> bool:
        pass

    @abstractmethod
    async def create_table(self, table: str, schema: dict[str, str]) -> bool:
        pass


class DashboardInterface(ABC):
    @abstractmethod
    async def render(self, widgets: list[dict]) -> dict:
        pass

    @abstractmethod
    async def update_widget(self, widget_id: str, data: Any) -> bool:
        pass


class ReportGeneratorInterface(ABC):
    @abstractmethod
    async def generate(self, template: str, data: dict) -> bytes:
        pass

    @abstractmethod
    async def list_templates(self) -> list[str]:
        pass
