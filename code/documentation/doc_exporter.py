from __future__ import annotations

import logging


class DocExporter:
    """Exports documentation to various output formats."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.documentation.exporter")

    def export_html(self, source_dir: str, output_dir: str) -> None:
        raise NotImplementedError

    def export_pdf(self, source_dir: str, output_path: str) -> None:
        raise NotImplementedError

    def export_json(self, source_dir: str, output_path: str) -> None:
        raise NotImplementedError
