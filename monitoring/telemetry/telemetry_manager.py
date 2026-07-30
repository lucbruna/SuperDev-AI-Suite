from __future__ import annotations

import logging
import time
from typing import Any

from .telemetry_event import TelemetryEvent
from .telemetry_sampler import TelemetrySampler
from .telemetry_batch import TelemetryBatcher
from .telemetry_exporter import TelemetryExporter
from .telemetry_filter import TelemetryFilter
from .telemetry_context import TelemetryContext


class TelemetryManager:
    """Central manager for telemetry data collection and routing."""

    def __init__(
        self,
        sampler: TelemetrySampler | None = None,
        batcher: TelemetryBatcher | None = None,
        exporter: TelemetryExporter | None = None,
        filter_: TelemetryFilter | None = None,
        context_provider: TelemetryContext | None = None,
    ) -> None:
        self._sampler = sampler or TelemetrySampler()
        self._batcher = batcher or TelemetryBatcher()
        self._exporter = exporter or TelemetryExporter()
        self._filter = filter_ or TelemetryFilter()
        self._context = context_provider or TelemetryContext()
        self._logger = logging.getLogger("superdev.telemetry")
        self._started = False

    def start(self) -> None:
        self._started = True
        self._logger.info("Telemetry manager started")

    def stop(self) -> None:
        self._started = False
        self._batcher.flush()
        self._logger.info("Telemetry manager stopped")

    def record(self, name: str, data: dict[str, Any] | None = None) -> None:
        if not self._started:
            return

        event = TelemetryEvent(
            name=name,
            data=data or {},
            context=self._context.get_context(),
            timestamp=time.time(),
        )

        if not self._filter.should_record(event):
            return

        if not self._sampler.should_sample(event):
            return

        self._batcher.add(event)

    def flush(self) -> None:
        self._batcher.flush()

    @property
    def context(self) -> TelemetryContext:
        return self._context
