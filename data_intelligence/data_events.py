"""Event bus for Data Intelligence Engine lifecycle events."""

from __future__ import annotations

import logging
from enum import Enum
from typing import Any, Callable


class DataIntelligenceEventType(Enum):
    INGESTION_STARTED = "ingestion.started"
    INGESTION_COMPLETED = "ingestion.completed"
    INGESTION_FAILED = "ingestion.failed"
    PIPELINE_STARTED = "pipeline.started"
    PIPELINE_COMPLETED = "pipeline.completed"
    PIPELINE_FAILED = "pipeline.failed"
    PIPELINE_RECOVERED = "pipeline.recovered"
    MODEL_TRAINED = "model.trained"
    MODEL_DEPLOYED = "model.deployed"
    PREDICTION_MADE = "prediction.made"
    REPORT_GENERATED = "report.generated"
    DASHBOARD_UPDATED = "dashboard.updated"
    GOVERNANCE_ACTION = "governance.action"


class DataIntelligenceEvents:
    """Lightweight in-process pub/sub."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.data_intelligence.events")
        self._listeners: dict[DataIntelligenceEventType,
                              list[Callable[[dict[str, Any]], None]]] = {}

    def on(self, event_type: DataIntelligenceEventType,
           listener: Callable[[dict[str, Any]], None]) -> None:
        self._listeners.setdefault(event_type, []).append(listener)

    def off(self, event_type: DataIntelligenceEventType,
            listener: Callable[[dict[str, Any]], None]) -> None:
        listeners = self._listeners.get(event_type, [])
        if listener in listeners:
            listeners.remove(listener)

    def publish(self, event_type: DataIntelligenceEventType,
                data: dict[str, Any] | None = None) -> None:
        payload = {"type": event_type.value, **(data or {})}
        for listener in list(self._listeners.get(event_type, [])):
            try:
                listener(payload)
            except Exception as exc:  # noqa: BLE001
                self._log.warning("listener failed for %s: %s",
                                  event_type.value, exc)

    def once(self, event_type: DataIntelligenceEventType,
             listener: Callable[[dict[str, Any]], None]) -> None:
        def wrapper(data: dict[str, Any]) -> None:
            self.off(event_type, wrapper)
            listener(data)

        self.on(event_type, wrapper)

    def listener_count(self, event_type: DataIntelligenceEventType) -> int:
        return len(self._listeners.get(event_type, []))
