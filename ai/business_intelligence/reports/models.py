"""Report models."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


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
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class ReportTemplate:
    template_id: str
    name: str
    report_type: ReportType = ReportType.CUSTOM
    sections: list[ReportSection] = field(default_factory=list)
    parameters: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class GeneratedReport:
    report_id: str
    template_id: str
    format: ReportFormat = ReportFormat.HTML
    data: Any = None
    file_path: str | None = None
    generated_at: datetime = field(default_factory=datetime.now)
    size_bytes: int = 0
    error: str | None = None


@dataclass
class ReportSchedule:
    schedule_id: str
    template_id: str
    frequency: ScheduleFrequency = ScheduleFrequency.WEEKLY
    recipients: list[str] = field(default_factory=list)
    format: ReportFormat = ReportFormat.PDF
    enabled: bool = True
    last_run: datetime | None = None
    next_run: datetime | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
