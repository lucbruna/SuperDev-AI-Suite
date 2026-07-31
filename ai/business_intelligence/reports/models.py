"""Report models."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum


class ReportFormat(Enum):
    PDF = "pdf"
    HTML = "html"
    CSV = "csv"
    JSON = "json"
    XLSX = "xlsx"


class ReportType(Enum):
    EXECUTIVE = "executive"
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    SALES = "sales"
    MARKETING = "marketing"
    CUSTOM = "custom"


class ScheduleFrequency(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


@dataclass
class ReportSection:
    section_id: str
    title: str
    content: Any = None
    section_type: str = "text"
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReportTemplate:
    template_id: str
    name: str
    report_type: ReportType = ReportType.CUSTOM
    sections: List[ReportSection] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class GeneratedReport:
    report_id: str
    template_id: str
    format: ReportFormat = ReportFormat.HTML
    data: Any = None
    file_path: Optional[str] = None
    generated_at: datetime = field(default_factory=datetime.now)
    size_bytes: int = 0
    error: Optional[str] = None


@dataclass
class ReportSchedule:
    schedule_id: str
    template_id: str
    frequency: ScheduleFrequency = ScheduleFrequency.WEEKLY
    recipients: List[str] = field(default_factory=list)
    format: ReportFormat = ReportFormat.PDF
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
