"""Reporting subsystem (Volume 22).

Executive, financial and operational reports rendered as JSON, Markdown,
HTML or CSV, with cron-based scheduling.
"""

from __future__ import annotations

from data_intelligence.reporting.base import (ReportRenderer,
                                              ReportingError)
from data_intelligence.reporting.engine import ReportingEngine
from data_intelligence.reporting.formats import (CsvRenderer, HtmlRenderer,
                                                 JsonRenderer,
                                                 MarkdownRenderer,
                                                 RENDERERS, render_report)
from data_intelligence.reporting.scheduler import ReportScheduler
from data_intelligence.reporting.templates import (ReportTemplate,
                                                   TEMPLATES, get_template)

__all__ = [
    "ReportingEngine", "ReportScheduler", "ReportTemplate", "ReportRenderer",
    "ReportingError", "JsonRenderer", "MarkdownRenderer", "HtmlRenderer",
    "CsvRenderer", "RENDERERS", "render_report", "TEMPLATES", "get_template",
]
