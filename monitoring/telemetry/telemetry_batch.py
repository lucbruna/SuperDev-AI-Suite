from __future__ import annotations

import logging
import time
from typing import Any

from .telemetry_event import TelemetryEvent
from .telemetry_exporter import TelemetryExporter


class TelemetryBatcher:
    """Batches telemetry events before exporting."""

    def __init__(
        self,
        exporter: TelemetryExporter | None = None,
        batch_size: int = 100,
        flush_interval: float = 5.0,
    ) -> None:
        self._exporter = exporter or TelemetryExporter()
        self._batch_size = batch_size
        self._flush_interval = flush_interval
        self._batch: list[TelemetryEvent] = []
        self._last_flush = time.time()
        self._logger = logging.getLogger("superdev.telemetry.batcher")

    def add(self, event: TelemetryEvent) -> None:
        self._batch.append(event)
        if len(self._batch) >= self._batch_size:
            self.flush()
        elif time.time() - self._last_flush >= self._flush_interval:
            self.flush()

    def flush(self) -> None:
        if not self._batch:
            return
        try:
            self._exporter.export(self._batch)
        except Exception as e:
            self._logger.error("Batch export failed: %s", e)
        self._batch.clear()
        self._last_flush = time.time()
