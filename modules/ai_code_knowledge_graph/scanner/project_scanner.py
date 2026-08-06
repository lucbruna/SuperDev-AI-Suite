"""Project scanner — top-level entry point of the scanner package.

Walks the repository, reads every indexable file and dispatches it to the
per-language content scanner for its category. Produces the scan result
consumed by the knowledge pipeline::

    {"project_root": str, "files": [...], "errors": [...], "stats": {...}}

where every file entry carries a ``parsed`` payload with ``entities``.
Per-language parsers are imported lazily: each content scanner falls back to
a lightweight stub until its dedicated parser ships in a later phase, so the
module stays import-clean and runnable at every build stage.
"""
from __future__ import annotations

import importlib
import logging
from pathlib import Path
from typing import Any

from modules.ai_code_knowledge_graph.config.scanner_config import ScannerConfig
from modules.ai_code_knowledge_graph.core.exceptions import ScanError
from modules.ai_code_knowledge_graph.scanner import filesystem_scanner

logger = logging.getLogger(__name__)

# Dispatch table: filesystem category -> scanner module name.
_LANGUAGE_SCANNER: dict[str, str] = {
    "python": "python_scanner",
    "javascript": "javascript_scanner",
    "typescript": "typescript_scanner",
    "json": "json_scanner",
    "yaml": "yaml_scanner",
    "xml": "xml_scanner",
    "markdown": "markdown_scanner",
    "docker": "docker_scanner",
    "git": "git_scanner",
    "plugin": "plugin_scanner",
    "workflow": "workflow_scanner",
    "database": "database_scanner",
}


class ProjectScanner:
    """Scans a project root into file entries with parsed payloads."""

    def __init__(self, config: ScannerConfig | None = None) -> None:
        self.config = config or ScannerConfig.from_env()

    def scan(self, project_root: str | None = None) -> dict[str, Any]:
        """Scan the project and return files, errors and stats."""
        config = self.config
        config.resolve(project_root)
        root = Path(config.project_root)
        if not root.is_dir():
            raise ScanError(f"Project root is not a directory: {config.project_root}")

        entries: list[dict[str, Any]] = []
        errors: list[dict[str, str]] = []
        by_language: dict[str, int] = {}

        for info in filesystem_scanner.scan_files(config):
            by_language[info.language] = by_language.get(info.language, 0) + 1
            entry, error = self._scan_file(root, info)
            if entry is not None:
                entries.append(entry)
            if error is not None:
                errors.append(error)

        stats: dict[str, Any] = {
            "files": len(entries),
            "errors": len(errors),
            "by_language": dict(sorted(by_language.items())),
            "total_size": sum(entry["size"] for entry in entries),
        }
        return {
            "project_root": config.project_root,
            "files": entries,
            "errors": errors,
            "stats": stats,
        }

    def _scan_file(
        self, root: Path, info: filesystem_scanner.FileInfo
    ) -> tuple[dict[str, Any] | None, dict[str, str] | None]:
        """Read one file and produce its entry; failures become error records."""
        if info.language not in _LANGUAGE_SCANNER:
            logger.debug("No scanner for category %r, skipping %s", info.language, info.rel_path)
            return None, None
        try:
            text = _read_text(root / info.rel_path, info.size)
        except OSError as exc:
            return None, {"rel_path": info.rel_path, "error": f"unreadable: {exc}"}
        if text is None:
            return None, {"rel_path": info.rel_path, "error": "binary or unreadable content"}
        try:
            scanner = _load_scanner(info.language)
            parsed = scanner.scan(text, info.rel_path)
        except ScanError as exc:
            return None, {"rel_path": info.rel_path, "error": exc.message}
        except Exception as exc:  # noqa: BLE001 — keep scanning the rest
            logger.warning("Scanner failed for %s: %s", info.rel_path, exc)
            return None, {"rel_path": info.rel_path, "error": f"{type(exc).__name__}: {exc}"}
        return {
            "rel_path": info.rel_path,
            "language": info.language,
            "size": info.size,
            "mtime": info.mtime,
            "parsed": parsed,
        }, None


def _load_scanner(language: str):
    module_name = _LANGUAGE_SCANNER.get(language)
    if module_name is None:
        raise ScanError(f"No content scanner for category '{language}'")
    return importlib.import_module(f"modules.ai_code_knowledge_graph.scanner.{module_name}")


def _read_text(path: Path, size: int, max_line_length: int = 1000) -> str | None:
    """Read a file as text; return None when the content looks binary."""
    if size == 0:
        return ""
    with open(path, "rb") as handle:
        raw = handle.read()
    if b"\x00" in raw:
        return None
    text = raw.decode("utf-8", errors="replace")
    if max_line_length > 0 and any(len(line) > max_line_length for line in text.splitlines()):
        lines = [
            line if len(line) <= max_line_length else line[:max_line_length] + "..."
            for line in text.splitlines()
        ]
        text = "\n".join(lines)
    return text
