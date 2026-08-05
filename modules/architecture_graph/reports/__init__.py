"""Reports: human-readable architecture, dependency and documentation reports.

All reports are generated as markdown and can be exported to HTML and (when a
renderer is available) PDF. Everything is stdlib-only with graceful fallbacks.
"""
from __future__ import annotations

from modules.architecture_graph.reports.architecture_report import (
    ArchitectureReport,
    architecture_report,
)
from modules.architecture_graph.reports.dependency_report import (
    DependencyReport,
    dependency_report,
)
from modules.architecture_graph.reports.documentation_generator import (
    DocumentationGenerator,
    generate_documentation,
)
from modules.architecture_graph.reports.html_report import (
    to_html_report,
    to_dict as html_to_dict,
    write_html_report,
)
from modules.architecture_graph.reports.pdf_report import (
    to_pdf as pdf_to_dict,
    write_pdf_report,
)

__all__ = [
    "ArchitectureReport",
    "DependencyReport",
    "DocumentationGenerator",
    "architecture_report",
    "dependency_report",
    "generate_documentation",
    "html_to_dict",
    "pdf_to_dict",
    "to_html_report",
    "write_html_report",
    "write_pdf_report",
]
