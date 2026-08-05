"""PNG/PDF rendering via the ``dot`` binary (graphviz), with SVG fallback.

When ``dot`` is unavailable the exporters degrade to returning the SVG source
with a note — the module never hard-depends on graphviz being installed.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from modules.architecture_graph.exports.graphviz import to_dot
from modules.architecture_graph.exports.svg import to_svg
from modules.architecture_graph.graph.graph_builder import ArchitectureGraph


def _dot_available() -> bool:
    return shutil.which("dot") is not None


def render_dot(graph: ArchitectureGraph, fmt: str) -> bytes | None:
    """Render the DOT source with graphviz. Returns None when unavailable."""
    if not _dot_available():
        return None
    dot = to_dot(graph).encode("utf-8")
    try:
        proc = subprocess.run(
            ["dot", f"-T{fmt}"],
            input=dot,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=120,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return proc.stdout if proc.returncode == 0 else None


def to_png(graph: ArchitectureGraph) -> dict[str, Any]:
    data = render_dot(graph, "png")
    if data is None:
        return {
            "format": "png",
            "rendered": False,
            "fallback": "svg",
            "message": "graphviz 'dot' not available; use svg instead",
            "data": None,
            "svg": to_svg(graph),
        }
    return {"format": "png", "rendered": True, "data": list(data), "size": len(data)}


def to_pdf(graph: ArchitectureGraph) -> dict[str, Any]:
    data = render_dot(graph, "pdf")
    if data is None:
        return {
            "format": "pdf",
            "rendered": False,
            "fallback": "svg",
            "message": "graphviz 'dot' not available; use svg instead",
            "data": None,
            "svg": to_svg(graph),
        }
    return {"format": "pdf", "rendered": True, "data": list(data), "size": len(data)}


def export_file(
    graph: ArchitectureGraph, fmt: str, dest: str | Path
) -> dict[str, Any]:
    """Render and write an image file to disk. Returns a status dict."""
    dest_path = Path(dest)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    if fmt == "png":
        result = to_png(graph)
    elif fmt == "pdf":
        result = to_pdf(graph)
    elif fmt == "svg":
        result = {"format": "svg", "rendered": True, "source": to_svg(graph)}
    else:
        return {"format": fmt, "rendered": False, "message": f"unsupported: {fmt}"}

    if result.get("rendered") and result.get("data") is not None:
        dest_path.write_bytes(bytes(result["data"]))
    elif result.get("source"):
        dest_path.write_text(result["source"], encoding="utf-8")
    else:
        return {**result, "message": "rendering unavailable; nothing written"}

    return {**result, "path": str(dest_path), "message": "written"}
