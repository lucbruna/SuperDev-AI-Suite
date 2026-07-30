from __future__ import annotations

from typing import Any


class MonitoringRegistry:
    """Registry for monitoring components — collectors, exporters, alerts, etc."""

    def __init__(self) -> None:
        self._collectors: dict[str, Any] = {}
        self._exporters: dict[str, Any] = {}
        self._alert_channels: dict[str, Any] = {}
        self._health_checks: dict[str, Any] = {}
        self._profilers: dict[str, Any] = {}
        self._anomaly_detectors: dict[str, Any] = {}

    def register_collector(self, name: str, collector: Any) -> None:
        self._collectors[name] = collector

    def register_exporter(self, name: str, exporter: Any) -> None:
        self._exporters[name] = exporter

    def register_alert_channel(self, name: str, channel: Any) -> None:
        self._alert_channels[name] = channel

    def register_health_check(self, name: str, check: Any) -> None:
        self._health_checks[name] = check

    def register_profiler(self, name: str, profiler: Any) -> None:
        self._profilers[name] = profiler

    def register_anomaly_detector(self, name: str, detector: Any) -> None:
        self._anomaly_detectors[name] = detector

    def get_collector(self, name: str) -> Any:
        return self._collectors.get(name)

    def get_exporter(self, name: str) -> Any:
        return self._exporters.get(name)

    def list_collectors(self) -> list[str]:
        return list(self._collectors.keys())

    def list_exporters(self) -> list[str]:
        return list(self._exporters.keys())

    def all_health_checks(self) -> dict[str, Any]:
        return dict(self._health_checks)


__all__ = ["MonitoringRegistry"]
