"""Report templates (executive, financial, operational)."""

from __future__ import annotations

from typing import Any

from data_intelligence.data_models import ReportSpec


class ReportTemplate:
    """A named report layout with placeholder sections."""

    def __init__(self, name: str, sections: list[dict[str, Any]]) -> None:
        self.name = name
        self.sections = sections

    def instantiate(self, data: dict[str, Any]) -> dict[str, Any]:
        """Fills the template with the given section data."""
        filled: list[dict[str, Any]] = []
        for section in self.sections:
            key = section.get("key")
            title = section.get("title", key or "")
            filled.append({"key": key, "title": title,
                           "data": data.get(key) if key else None})
        return {"name": self.name, "sections": filled}


TEMPLATES: dict[str, ReportTemplate] = {
    "executive": ReportTemplate("executive", [
        {"key": "summary", "title": "Resumo executivo"},
        {"key": "indicators", "title": "Indicadores-chave"},
        {"key": "recommendations", "title": "Recomendações"},
    ]),
    "financial": ReportTemplate("financial", [
        {"key": "revenue", "title": "Receita"},
        {"key": "costs", "title": "Custos"},
        {"key": "margin", "title": "Margem"},
    ]),
    "operational": ReportTemplate("operational", [
        {"key": "throughput", "title": "Volume processado"},
        {"key": "errors", "title": "Erros"},
        {"key": "latency", "title": "Latência"},
    ]),
}


def get_template(report_type: str) -> ReportTemplate | None:
    return TEMPLATES.get(report_type)
