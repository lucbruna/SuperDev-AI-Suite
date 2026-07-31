"""Events for the DevOps & Cloud Infrastructure Engine (Volume 37)."""

from __future__ import annotations

from enum import Enum
from typing import Any, Callable

from devops_engine.devops_logger import get_logger

_Listener = Callable[[dict[str, Any]], None]


class DevopsEventType(Enum):
    RESOURCE_PROVISIONED = "devops.resource.provisioned"
    RESOURCE_TERMINATED = "devops.resource.terminated"
    RESOURCE_FAILED = "devops.resource.failed"
    CONTAINER_CREATED = "devops.container.created"
    CONTAINER_STARTED = "devops.container.started"
    CONTAINER_STOPPED = "devops.container.stopped"
    CONTAINER_FAILED = "devops.container.failed"
    IMAGE_BUILT = "devops.image.built"
    IMAGE_PUSHED = "devops.image.pushed"
    CLUSTER_READY = "devops.cluster.ready"
    CLUSTER_DEGRADED = "devops.cluster.degraded"
    DEPLOYMENT_CREATED = "devops.deployment.created"
    DEPLOYMENT_COMPLETED = "devops.deployment.completed"
    DEPLOYMENT_FAILED = "devops.deployment.failed"
    DEPLOYMENT_ROLLED_BACK = "devops.deployment.rolled_back"
    SERVICE_CREATED = "devops.service.created"
    PIPELINE_STARTED = "devops.pipeline.started"
    PIPELINE_SUCCEEDED = "devops.pipeline.succeeded"
    PIPELINE_FAILED = "devops.pipeline.failed"
    PIPELINE_CANCELLED = "devops.pipeline.cancelled"
    BUILD_SUCCEEDED = "devops.build.succeeded"
    BUILD_FAILED = "devops.build.failed"
    RELEASE_DEPLOYED = "devops.release.deployed"
    RELEASE_ROLLED_BACK = "devops.release.rolled_back"
    HEALTH_CHECKED = "devops.health.checked"
    HEALTH_DEGRADED = "devops.health.degraded"
    HEALTH_RECOVERED = "devops.health.recovered"
    ANOMALY_DETECTED = "devops.anomaly.detected"
    ALERT_RAISED = "devops.alert.raised"
    ALERT_RESOLVED = "devops.alert.resolved"
    LOG_COLLECTED = "devops.log.collected"
    BACKUP_STARTED = "devops.backup.started"
    BACKUP_SUCCEEDED = "devops.backup.succeeded"
    BACKUP_FAILED = "devops.backup.failed"
    SNAPSHOT_CREATED = "devops.snapshot.created"
    RESTORE_STARTED = "devops.restore.started"
    RESTORE_SUCCEEDED = "devops.restore.succeeded"
    RESTORE_FAILED = "devops.restore.failed"
    INCIDENT_DETECTED = "devops.incident.detected"
    INCIDENT_RESOLVED = "devops.incident.resolved"
    FAILOVER_ACTIVATED = "devops.failover.activated"
    SCALED_UP = "devops.scaled.up"
    SCALED_DOWN = "devops.scaled.down"
    COST_RECORDED = "devops.cost.recorded"
    COST_RECOMMENDATION = "devops.cost.recommendation"


class DevopsEvents:
    """Thread-safe pub/sub event bus with listener isolation."""

    def __init__(self) -> None:
        self._log = get_logger("events")
        self._listeners: dict[DevopsEventType, list[_Listener]] = {}

    def on(self, event_type: DevopsEventType, listener: _Listener) -> None:
        self._listeners.setdefault(event_type, []).append(listener)

    def once(self, event_type: DevopsEventType, listener: _Listener) -> None:
        def _wrapper(payload: dict[str, Any]) -> None:
            self.off(event_type, _wrapper)
            listener(payload)

        self.on(event_type, _wrapper)

    def off(self, event_type: DevopsEventType, listener: _Listener) -> None:
        listeners = self._listeners.get(event_type)
        if listeners is not None and listener in listeners:
            listeners.remove(listener)

    def publish(self, event_type: DevopsEventType,
                payload: dict[str, Any]) -> None:
        for listener in list(self._listeners.get(event_type, [])):
            try:
                listener(payload)
            except Exception:  # noqa: BLE001 - listener isolation
                self._log.warning("listener failed for %s: %s",
                                  event_type.value, listener)
