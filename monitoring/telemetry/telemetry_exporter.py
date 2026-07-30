from __future__ import annotations

import logging
from typing import Any

from .telemetry_event import TelemetryEvent


class TelemetryExporter:
    """Exports telemetry events to a destination."""

    def __init__(self) -> None:
        self._logger = logging.getLogger("superdev.telemetry.exporter")

    def export(self, events: list[TelemetryEvent]) -> None:
        for event in events:
            self._logger.debug("Telemetry: %s", event.name)
