"""PDF report: render the HTML report to PDF via headless tools.

Strategy, in order of preference:
1. ``weasyprint`` (if installed) — direct HTML -> PDF.
2. ``wkhtmltopdf`` binary (if on PATH).
3. Fallback: write the HTML file and instruct the user to print to PDF.

The report writer always succeeds; the PDF step is best-effort.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from modules.architecture_graph.graph.graph_builder import ArchitectureGraph
from modules.architecture_graph.reports.html_report import to_html_report


def _has_weasyprint() -> bool:
    try:
        import weasyprint  # type: ignore  # noqa: F401

        return True
    except ImportError:
        return False


def to_pdf(graph: ArchitectureGraph, title: str = "Architecture Report") -> dict[str, Any]:
    """Return the PDF bytes (or a fallback explanation)."""
    html_source = to_html_report(graph, title)

    if _has_weasyprint():
        try:
            from weasyprint import HTML  # type: ignore

            data = HTML(string=html_source).write_pdf()
            return {"format": "pdf", "rendered": True, "data": list(data), "size": len(data)}
        except Exception:
            pass

    wkhtml = shutil.which("wkhtmltopdf")
    if wkhtml:
        try:
            with tempfile.TemporaryDirectory() as tmp:
                html_path = Path(tmp) / "report.html"
                pdf_path = Path(tmp) / "report.pdf"
                html_path.write_text(html_source, encoding="utf-8")
                proc = subprocess.run(
                    [wkhtml, "-q", str(html_path), str(pdf_path)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=120,
                )
                if proc.returncode == 0 and pdf_path.exists():
                    data = pdf_path.read_bytes()
                    return {"format": "pdf", "rendered": True, "data": list(data), "size": len(data)}
        except (OSError, subprocess.SubprocessError):
            pass

    return {
        "format": "pdf",
        "rendered": False,
        "message": "no PDF renderer available (weasyprint or wkhtmltopdf); "
        "the HTML report is available instead",
        "html": html_source,
    }


def write_pdf_report(graph: ArchitectureGraph, path: str, title: str = "Architecture Report") -> dict[str, Any]:
    result = to_pdf(graph, title)
    dest = Path(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if result.get("rendered") and result.get("data") is not None:
        dest.write_bytes(bytes(result["data"]))
        return {**result, "path": str(dest), "message": "written"}
    # Fallback: write the HTML next to the requested PDF path.
    html_path = dest.with_suffix(".html")
    html_path.write_text(result.get("html", ""), encoding="utf-8")
    return {**result, "path": str(html_path), "message": "PDF unavailable; wrote HTML fallback"}
