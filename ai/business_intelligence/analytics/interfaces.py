"""Analytics engine interfaces."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
from .models import AnalysisRequest, AnalysisResult, DataPoint, Insight


class AnalyticsEngineInterface(ABC):
    @abstractmethod
    async def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        pass

    @abstractmethod
    async def ingest_data(self, data_points: List[DataPoint]) -> bool:
        pass

    @abstractmethod
    async def get_insights(self, time_range: Optional[tuple] = None) -> List[Insight]:
        pass


class DataWarehouseInterface(ABC):
    @abstractmethod
    async def query(self, sql: str, params: Optional[Dict] = None) -> List[Dict]:
        pass

    @abstractmethod
    async def store(self, table: str, records: List[Dict]) -> bool:
        pass

    @abstractmethod
    async def create_table(self, table: str, schema: Dict[str, str]) -> bool:
        pass


class DashboardInterface(ABC):
    @abstractmethod
    async def render(self, widgets: List[Dict]) -> Dict:
        pass

    @abstractmethod
    async def update_widget(self, widget_id: str, data: Any) -> bool:
        pass


class ReportGeneratorInterface(ABC):
    @abstractmethod
    async def generate(self, template: str, data: Dict) -> bytes:
        pass

    @abstractmethod
    async def list_templates(self) -> List[str]:
        pass
