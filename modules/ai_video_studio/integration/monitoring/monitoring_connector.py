"""Monitoring Connector — facade over the enterprise monitors."""
from __future__ import annotations

from typing import Any

from modules.ai_video_studio.integration.connector_base import DomainConnector
from modules.ai_video_studio.integration.monitoring.gpu_monitor import get_gpu_monitor
from modules.ai_video_studio.integration.monitoring.metrics_collector import (
    get_metrics_collector,
)
from modules.ai_video_studio.integration.monitoring.render_monitor import (
    get_render_monitor,
)
from modules.ai_video_studio.integration.monitoring.resource_monitor import (
    get_resource_monitor,
)
from modules.ai_video_studio.integration.monitoring.storage_monitor import (
    get_storage_monitor,
)


class MonitoringConnector(DomainConnector):
    """Collects metrics and monitors resources, GPU, render and storage."""

    domain = "monitoring"
    description = "Metrics collection and resource/GPU/render/storage monitoring"

    def __init__(self) -> None:
        super().__init__()
        self._register("metrics", lambda d: get_metrics_collector().snapshot())
        self._register("resources", lambda d: get_resource_monitor().collect())
        self._register("gpu", lambda d: get_gpu_monitor().collect())
        self._register("render", lambda d: get_render_monitor().collect())
        self._register("storage", lambda d: get_storage_monitor().collect())
        self._register("record", self._record)

    def _record(self, data: dict[str, Any]) -> dict[str, Any]:
        name = data.get("name", "op")
        get_metrics_collector().increment(name)
        if "seconds" in data:
            get_metrics_collector().timing(name, float(data["seconds"]))
        return {"ok": True, "recorded": name}


_monitoring_connector: MonitoringConnector | None = None


def get_monitoring_connector() -> MonitoringConnector:
    global _monitoring_connector
    if _monitoring_connector is None:
        _monitoring_connector = MonitoringConnector()
    return _monitoring_connector
