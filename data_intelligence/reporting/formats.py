"""Report format renderers (JSON, Markdown, HTML, CSV)."""

from __future__ import annotations

import csv
import io
import json
from typing import Any

from data_intelligence.data_models import ReportFormat
from data_intelligence.reporting.base import (ReportRenderer,
                                              ReportingError)


class JsonRenderer(ReportRenderer):
    def render(self, report_format: ReportFormat,
               report: dict[str, Any]) -> str:
        return json.dumps(report, ensure_ascii=False, indent=2)


class MarkdownRenderer(ReportRenderer):
    def render(self, report_format: ReportFormat,
               report: dict[str, Any]) -> str:
        lines = [f"# {report.get('name', 'Relatório')}", ""]
        summary = report.get("summary", {})
        if summary:
            lines.append("## Resumo")
            for key, value in summary.items():
                lines.append(f"- **{key}**: {value}")
            lines.append("")
        tables = report.get("tables", [])
        for table in tables:
            lines.append(f"## {table.get('title', 'Tabela')}")
            lines.append("")
            columns = table.get("columns", [])
            rows = table.get("rows", [])
            if columns:
                lines.append("| " + " | ".join(columns) + " |")
                lines.append("|" + "|".join(["---"] * len(columns)) + "|")
                for row in rows:
                    cells = [str(row.get(col, "")) for col in columns]
                    lines.append("| " + " | ".join(cells) + " |")
            lines.append("")
        return "\n".join(lines)


class HtmlRenderer(ReportRenderer):
    def render(self, report_format: ReportFormat,
               report: dict[str, Any]) -> str:
        tables_html = []
        for table in report.get("tables", []):
            columns = table.get("columns", [])
            rows = table.get("rows", [])
            header = "".join(f"<th>{c}</th>" for c in columns)
            body = "".join(
                "<tr>" + "".join(
                    f"<td>{row.get(col, '')}</td>" for col in columns)
                + "</tr>" for row in rows)
            tables_html.append(
                f"<h2>{table.get('title', 'Tabela')}</h2>"
                f"<table><thead><tr>{header}</tr></thead>"
                f"<tbody>{body}</tbody></table>")
        summary_html = "".join(
            f"<p><strong>{k}</strong>: {v}</p>"
            for k, v in report.get("summary", {}).items())
        return (f"<html><body><h1>{report.get('name', 'Relatório')}</h1>"
                f"{summary_html}{''.join(tables_html)}</body></html>")


class CsvRenderer(ReportRenderer):
    def render(self, report_format: ReportFormat,
               report: dict[str, Any]) -> str:
        tables = report.get("tables", [])
        if not tables:
            return ""
        table = tables[0]
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=table.get("columns", []))
        writer.writeheader()
        writer.writerows(table.get("rows", []))
        return buffer.getvalue()


RENDERERS: dict[ReportFormat, ReportRenderer] = {
    ReportFormat.JSON: JsonRenderer(),
    ReportFormat.MARKDOWN: MarkdownRenderer(),
    ReportFormat.HTML: HtmlRenderer(),
    ReportFormat.CSV: CsvRenderer(),
}


def render_report(report_format: ReportFormat,
                  report: dict[str, Any]) -> str:
    renderer = RENDERERS.get(report_format)
    if renderer is None:
        raise ReportingError(f"unsupported format: {report_format}")
    return renderer.render(report_format, report)
