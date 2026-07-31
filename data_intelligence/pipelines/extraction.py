"""Pipeline extraction stage (source -> raw records)."""

from __future__ import annotations

from typing import Any

from data_intelligence.pipelines.base import PipelineError, PipelineStage


class ExtractionStage(PipelineStage):
    """Fetches raw records from a registered ingestion source.

    Config:
        * ``collector`` - the ingestion collector (required).
        * ``source_id`` - the source to extract from.
    """

    stage_type = "extraction"

    def __init__(self, collector: Any = None, source_id: str = "",
                 **config: Any) -> None:
        super().__init__(collector=collector, source_id=source_id, **config)
        self.collector = collector
        self.source_id = source_id

    def run(self, records: list[dict[str, Any]],
            context: dict[str, Any]) -> tuple[list[dict[str, Any]],
                                              dict[str, Any]]:
        if self.collector is None or not self.source_id:
            raise PipelineError(
                "ExtractionStage requires collector and source_id")
        fetched = self.collector.fetch(self.source_id,
                                       tags=["extracted"])
        extracted = [dict(record.data) for record in fetched]
        context["extracted_count"] = len(extracted)
        return extracted, context
